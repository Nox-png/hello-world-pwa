from datetime import date
import json
import logging
import os
import re
import zipfile
from pathlib import Path
from typing import List, Dict, Any
from urllib import request, error

from django.db import connections
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from web.context_processors import versionnumber_processor
from helloworldpwa.Search_data import search_documents

robotsTxtContent = """\
# Rules for GPTBot:
User-Agent: GPTBot
Disallow: /

# Basic Rules for other User-Agents:
User-Agent: *
Disallow: /private/
Disallow: /junk/
"""

securityTxtContent = """\
Contact: mailto:security@testapp.de
Preferred-Languages: de, en
"""

health_logger = logging.getLogger('web.health')

def get_database_health():
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
        return True, None
    except Exception as error:
        return False, error

# Create your views here.
def index(request, template='web/base.html'):
    if not request.user.is_authenticated:
         return redirect("/accounts/login")
    return render(request, template)

@require_GET
@cache_page(60 * 60)  # Zwischenspeicherung für 1 Stunde
def robotsTXT(request):
    return HttpResponse(robotsTxtContent, content_type="text/plain")
@require_GET
def securityTXT(request):
    return HttpResponse(securityTxtContent, content_type="text/plain")

def health_check(request):
    database_ok, database_error = get_database_health()
    version_context = versionnumber_processor(None)

    response_payload = {
        "status": "healthy" if database_ok else "degraded",
        "timestamp": timezone.now().isoformat(),
        "app": {
            "version": version_context.get("versionnumber"),
            "build": version_context.get("buildNumber"),
        },
        "checks": {
            "database": "ok" if database_ok else "error",
        },
    }

    if database_error is not None:
        response_payload["checks"]["database_error"] = str(database_error)
        health_logger.error("health_check degraded: database check failed", extra={"path": request.path})
    else:
        health_logger.info("health_check healthy", extra={"path": request.path})

    return JsonResponse(response_payload, status=200 if database_ok else 503)

def offline(request, template='web/offline.html'):
    return render(request, template)


def _extract_document_text(file_path: str) -> str:
    """Extract readable text from common book formats when possible."""
    path = Path(file_path)
    if not path.exists():
        return ""

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        for module_name in ("pypdf", "PyPDF2"):
            try:
                module = __import__(module_name)
                reader = getattr(module, "PdfReader", None)
                if reader is None:
                    continue
                pages = reader(str(path)).pages
                text = "\n".join(page.extract_text() or "" for page in pages)
                return re.sub(r"\s+", " ", text).strip()
            except Exception:
                continue

    if suffix == ".docx":
        try:
            with zipfile.ZipFile(path) as archive:
                content = archive.read("word/document.xml").decode("utf-8", errors="ignore")
            text = re.sub(r"<[^>]+>", " ", content)
            return re.sub(r"\s+", " ", text).strip()
        except Exception:
            return ""

    if suffix == ".epub":
        try:
            with zipfile.ZipFile(path) as archive:
                names = [name for name in archive.namelist() if name.endswith((".html", ".xhtml", ".xml"))]
                chunks = []
                for name in names[:10]:
                    content = archive.read(name).decode("utf-8", errors="ignore")
                    chunks.append(re.sub(r"<[^>]+>", " ", content))
                return re.sub(r"\s+", " ", " ".join(chunks)).strip()
        except Exception:
            return ""

    return ""


def _build_problem_set_fallback(query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create a small problem set from a book query, with hints and solutions."""
    topic = (query or "general study").strip() or "general study"
    book_names = [document["name"] for document in documents[:3]]

    problems: List[Dict[str, Any]] = []
    for index in range(1, 11):
        title = f"Problem {index}: {topic.title()}"
        prompt = (
            f"Create a challenging practice question about {topic} that feels like it could come from a textbook or workbook."
        )
        if book_names:
            prompt += f" Use the explored material from {', '.join(book_names)} as inspiration."

        problems.append(
            {
                "number": index,
                "title": title,
                "prompt": prompt,
                "hint": f"Hint {index}: Break the problem into smaller steps and identify the key idea first.",
                "solution": f"Solution {index}: Work through the core concept carefully and check your reasoning against the main principle behind {topic}.",
            }
        )
    return problems


def _build_problem_set(query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate a mentor problem set from the book search results, using the OpenAI API when available."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _build_problem_set_fallback(query, documents)

    topic = (query or "general study").strip() or "general study"
    book_names = [document["name"] for document in documents[:5]]
    extracted_chunks = []
    for document in documents[:5]:
        text = _extract_document_text(document.get("path", ""))
        if text:
            extracted_chunks.append(f"{document['name']}: {text[:1800]}")

    context = "; ".join(extracted_chunks[:3]) if extracted_chunks else "; ".join(book_names) if book_names else "general study materials"

    payload = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        "messages": [
            {
                "role": "system",
                "content": "You are an expert tutor who creates challenging practice problems, hints, and solutions from textbook-style material.",
            },
            {
                "role": "user",
                "content": (
                    f"Create 10 challenging practice problems for the topic or book '{topic}'. "
                    f"Use these discovered book files as context: {context}. "
                    "Return valid JSON as an array of objects. Each object must have the keys: number, title, prompt, hint, solution."
                ),
            },
        ],
        "temperature": 0.7,
    }

    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

            parsed = json.loads(cleaned)
            if isinstance(parsed, list) and parsed:
                return parsed
    except (error.URLError, error.HTTPError, ValueError, KeyError, TimeoutError):
        pass

    return _build_problem_set_fallback(query, documents)


@require_http_methods(["GET"])
def document_search(request, template='web/document_search.html'):
    if not request.user.is_authenticated:
        return redirect("/accounts/login")

    query = (request.GET.get("q") or "").strip()
    search_root = (request.GET.get("root") or "").strip()
    results = []

    if query:
        results = search_documents(
            keyword=query,
            search_root=search_root or None,
            extensions=[".doc", ".docx", ".pdf", ".epub"],
        )

    return render(
        request,
        template,
        {
            "query": query,
            "search_root": search_root,
            "results": results,
        },
    )


@require_http_methods(["GET"])
def mentor(request, template='web/mentor.html'):
    if not request.user.is_authenticated:
        return redirect("/accounts/login")

    query = (request.GET.get("q") or "").strip()
    search_root = (request.GET.get("root") or "").strip()
    documents = []

    if query:
        documents = search_documents(
            keyword=query,
            search_root=search_root or None,
            extensions=[".doc", ".docx", ".pdf", ".epub"],
        )

    problems = _build_problem_set(query or "study", documents)

    return render(
        request,
        template,
        {
            "query": query,
            "search_root": search_root,
            "documents": documents,
            "problems": problems,
        },
    )
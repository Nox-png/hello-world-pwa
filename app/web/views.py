from datetime import date
import logging

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
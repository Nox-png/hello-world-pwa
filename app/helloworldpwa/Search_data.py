import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

SUPPORTED_EXTENSIONS = {".doc", ".docx", ".pdf", ".epub"}


def _normalize_keyword(keyword: Optional[str]) -> List[str]:
    """Split a user keyword into simple search tokens."""
    if not keyword:
        return []

    return [part.lower() for part in re.split(r"[\W_]+", keyword.strip()) if part]


def _matches_keyword(file_path: Path, keyword_tokens: Iterable[str]) -> bool:
    """Match the keyword against the file name and full path."""
    if not keyword_tokens:
        return True

    haystack = " ".join([file_path.name.lower(), str(file_path).lower()])
    return all(token in haystack for token in keyword_tokens)


def _get_search_roots(search_root: Optional[Union[str, os.PathLike, List[Union[str, os.PathLike]], Tuple[Union[str, os.PathLike], ...]]]) -> List[Path]:
    """Collect the locations that should be searched."""
    if search_root is None:
        candidates = [
            os.environ.get("ANDROID_STORAGE"),
            "/storage/emulated/0",
            "/sdcard",
            os.path.expanduser("~"),
        ]
    elif isinstance(search_root, (list, tuple, set)):
        candidates = list(search_root)
    else:
        candidates = [search_root]

    roots = []
    for candidate in candidates:
        if candidate:
            root = Path(candidate)
            if root.exists():
                roots.append(root)

    return roots


def search_documents(
    keyword: Optional[str] = None,
    search_root: Optional[Union[str, os.PathLike, List[Union[str, os.PathLike]], Tuple[Union[str, os.PathLike], ...]]] = None,
    extensions: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    """Search common document files on disk for a keyword match.

    The search looks for files such as .doc, .docx, .epub and .pdf and matches
    the user keyword against the file name and path. If no keyword is provided,
    all supported document files are returned.
    """

    allowed_extensions = {ext.lower() for ext in (extensions or SUPPORTED_EXTENSIONS)}
    keyword_tokens = _normalize_keyword(keyword)
    results: List[Dict[str, Any]] = []

    for root in _get_search_roots(search_root):
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            extension = path.suffix.lower()
            if extension not in allowed_extensions:
                continue

            if _matches_keyword(path, keyword_tokens):
                results.append(
                    {
                        "name": path.name,
                        "path": str(path),
                        "extension": extension,
                    }
                )

    return sorted(results, key=lambda item: item["name"].lower())


def search_phone_documents(keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience wrapper for scanning the common phone storage locations."""
    return search_documents(keyword=keyword)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search for books and exercise papers on disk")
    parser.add_argument("keyword", nargs="?", default="", help="Keyword to search for")
    parser.add_argument("--root", default=None, help="Optional directory to scan")
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=list(SUPPORTED_EXTENSIONS),
        help="File extensions to search for",
    )
    args = parser.parse_args()

    matches = search_documents(keyword=args.keyword, search_root=args.root, extensions=args.extensions)
    if not matches:
        print("No matching documents found.")
    else:
        for match in matches:
            print(f"{match['name']} -> {match['path']}")

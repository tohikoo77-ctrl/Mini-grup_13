import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin


METHODS = ("get", "post", "put", "patch", "delete")
BODY_METHODS = {"post", "put", "patch"}
EXCLUDED_PREFIXES = (
    "admin/",
    "__debug__/",
    "static/",
    "media/",
)


def setup_django():
    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src"

    import sys

    for path in (project_root, src_dir):
        path = str(path)
        if path not in sys.path:
            sys.path.insert(0, path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()


def route_to_postman_path(route):
    route = route.strip("^$")
    route = route.replace("\\Z", "").replace("\\z", "")
    route = route.replace("\\/", "/").replace("^", "").replace("$", "")
    route = route.lstrip("/")

    route = re.sub(r"<(?:[^:<>]+:)?([^<>]+)>", r":\1", route)
    route = re.sub(r"\(\?P<([^>]+)>[^)]+\)", r":\1", route)
    route = route.replace("?", "")

    return route


def url_with_variables(route):
    parts = [part for part in route.strip("/").split("/") if part]
    rendered = []
    for part in parts:
        if part.startswith(":"):
            rendered.append("{{" + part[1:] + "}}")
        else:
            rendered.append(part)
    return "/".join(rendered)


def route_name(route, method, name):
    clean = route.strip("/") or "root"
    clean = clean.replace("/", " ")
    clean = clean.replace("-", " ").replace("_", " ")
    title = " ".join(word.capitalize() for word in clean.split())
    if name:
        return f"{method.upper()} {title} ({name})"
    return f"{method.upper()} {title}"


def folder_name(route):
    parts = [part for part in route.strip("/").split("/") if part]
    if not parts:
        return "Root"
    if parts[0] == "api" and len(parts) > 1:
        return parts[1].replace("-", " ").replace("_", " ").title()
    return parts[0].replace("-", " ").replace("_", " ").title()


def callback_methods(callback):
    actions = getattr(callback, "actions", None)
    if actions:
        return sorted(method for method in actions if method in METHODS)

    view_class = getattr(callback, "cls", None)
    if view_class is not None:
        methods = []
        for method in METHODS:
            if hasattr(view_class, method):
                methods.append(method)
        return methods or ["get"]

    return ["get"]


def flatten_patterns(patterns, prefix=""):
    from django.urls.resolvers import URLPattern, URLResolver

    for pattern in patterns:
        current = route_to_postman_path(str(pattern.pattern))
        full_route = f"{prefix}{current}"

        if isinstance(pattern, URLResolver):
            yield from flatten_patterns(pattern.url_patterns, full_route)
            continue

        if not isinstance(pattern, URLPattern):
            continue

        route = full_route.strip("/")
        if not route:
            route = "/"
        if any(route.startswith(prefix.strip("/")) for prefix in EXCLUDED_PREFIXES):
            continue

        callback = pattern.callback
        for method in callback_methods(callback):
            yield {
                "route": route,
                "method": method.upper(),
                "name": route_name(route, method, pattern.name),
            }


def postman_item(endpoint):
    route = endpoint["route"]
    path = url_with_variables(route)
    raw_url = "{{base_url}}/" + path if path else "{{base_url}}"

    request = {
        "method": endpoint["method"],
        "header": [
            {
                "key": "Accept",
                "value": "application/json",
            },
            {
                "key": "Content-Type",
                "value": "application/json",
                "disabled": endpoint["method"] not in {"POST", "PUT", "PATCH"},
            },
            {
                "key": "Authorization",
                "value": "Bearer {{access_token}}",
                "type": "text",
                "disabled": True,
            },
        ],
        "url": {
            "raw": raw_url,
            "host": ["{{base_url}}"],
            "path": path.split("/") if path else [],
        },
    }

    if endpoint["method"].lower() in BODY_METHODS:
        request["body"] = {
            "mode": "raw",
            "raw": "{\n  \n}",
            "options": {
                "raw": {
                    "language": "json",
                }
            },
        }

    return {
        "name": endpoint["name"],
        "request": request,
        "response": [],
    }


def build_collection(endpoints, base_url):
    folders = {}
    for endpoint in sorted(endpoints, key=lambda item: (folder_name(item["route"]), item["route"], item["method"])):
        folders.setdefault(folder_name(endpoint["route"]), []).append(postman_item(endpoint))

    return {
        "info": {
            "name": "Mini Group 13 API",
            "description": "Auto-generated from Django URL patterns. Regenerate after changing urls.py.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {
                "key": "base_url",
                "value": base_url.rstrip("/"),
            },
            {
                "key": "access_token",
                "value": "",
            },
            {
                "key": "pk",
                "value": "1",
            },
            {
                "key": "id",
                "value": "1",
            },
            {
                "key": "slug",
                "value": "example",
            },
        ],
        "item": [
            {
                "name": name,
                "item": items,
            }
            for name, items in folders.items()
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Export Django URLs to a Postman collection.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL used in the Postman collection.",
    )
    parser.add_argument(
        "--output",
        default="postman/Mini-grup-13.postman_collection.json",
        help="Output JSON path.",
    )
    args = parser.parse_args()

    setup_django()

    from django.urls import get_resolver

    endpoints = list(flatten_patterns(get_resolver().url_patterns))
    collection = build_collection(endpoints, args.base_url)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(collection, indent=2), encoding="utf-8")

    print(f"Wrote {len(endpoints)} requests to {output_path}")
    print("Import this file in Postman.")


if __name__ == "__main__":
    main()

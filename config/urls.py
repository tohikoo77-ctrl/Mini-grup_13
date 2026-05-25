from importlib import import_module
from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


BASE_DIR = Path(__file__).resolve().parent.parent


def api_root(request):
    return JsonResponse(
        {
            "admin": "/admin/",
            "schema": "/api/schema/",
            "swagger": "/api/swagger/",
            "docs": "/api/docs/",
            "redoc": "/api/redoc/",
            "users": "/api/users/",
            "products": "/api/products/",
            "payments": "/api/payments/",
            "commerce_extras": "/api/commerce-extras/",
        }
    )


def swagger_not_configured(request):
    return JsonResponse(
        {
            "detail": (
                "Swagger is not configured because neither drf-spectacular nor "
                "drf-yasg is installed."
            )
        },
        status=501,
    )


def module_exists(module_path):
    try:
        import_module(module_path)
    except Exception:
        return False
    return True


urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/", api_root, name="api-root-api"),
    path("admin/", admin.site.urls),
]


_used_prefixes = set()


def add_include(prefix, module_path):
    if prefix in _used_prefixes:
        return
    if not module_exists(module_path):
        return

    urlpatterns.append(path(prefix, include(module_path)))
    _used_prefixes.add(prefix)


# Explicit routes for the known project apps. Both singular/plural and legacy
# aliases are kept so old frontend paths keep working while cleaner paths exist.
for url_prefix, url_module in [
    ("api/", "user.urls"),
    ("api/users/", "user.urls"),
    ("api/user/", "user.urls"),
    ("api/", "apps.user.urls"),
    ("api/users/", "apps.user.urls"),
    ("api/user/", "apps.user.urls"),
    ("api/products/", "product.urls"),
    ("api/product/", "product.urls"),
    ("api/payments/", "payment.urls"),
    ("api/payment/", "payment.urls"),
    ("api/commerce-extras/", "commerce_extras.urls"),
    ("api/commerce_extras/", "commerce_extras.urls"),
    ("api/extras/", "commerce_extras.urls"),
    ("api/commerce-extras/", "apps.commerce_extras.urls"),
    ("api/commerce_extras/", "apps.commerce_extras.urls"),
    ("api/extras/", "apps.commerce_extras.urls"),
]:
    add_include(url_prefix, url_module)


def discover_url_modules():
    ignored = {
        ".git",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        "__pycache__",
        "config",
        "media",
        "static",
        "staticfiles",
        "templates",
        "venv",
    }
    roots = [
        (BASE_DIR, ""),
        (BASE_DIR / "apps", "apps"),
        (BASE_DIR / "src" / "apps", "apps"),
    ]

    for root, prefix in roots:
        if not root.exists():
            continue

        for app_dir in sorted(root.iterdir()):
            if not app_dir.is_dir() or app_dir.name.startswith("_"):
                continue
            if app_dir.name in ignored:
                continue
            if not (app_dir / "__init__.py").exists():
                continue
            if not (app_dir / "urls.py").exists():
                continue

            module_name = f"{prefix}.{app_dir.name}.urls" if prefix else f"{app_dir.name}.urls"
            url_prefix = app_dir.name.replace("_", "-")
            yield f"api/{url_prefix}/", module_name


for url_prefix, url_module in discover_url_modules():
    add_include(url_prefix, url_module)


try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )
except ImportError:
    try:
        from drf_yasg import openapi
        from drf_yasg.views import get_schema_view
        from rest_framework import permissions
    except ImportError:
        urlpatterns += [
            path("api/schema/", swagger_not_configured, name="schema"),
            path("api/swagger/", swagger_not_configured, name="swagger-ui"),
            path("api/docs/", swagger_not_configured, name="docs"),
            path("api/redoc/", swagger_not_configured, name="redoc"),
            path("swagger/", swagger_not_configured, name="swagger"),
            path("docs/", swagger_not_configured, name="docs-short"),
            path("redoc/", swagger_not_configured, name="redoc-short"),
        ]
    else:
        schema_view = get_schema_view(
            openapi.Info(
                title="Mini Group 13 API",
                default_version="v1",
                description="API documentation",
            ),
            public=True,
            permission_classes=(permissions.AllowAny,),
        )
        urlpatterns += [
            path(
                "api/schema/",
                schema_view.without_ui(cache_timeout=0),
                name="schema",
            ),
            path(
                "api/swagger/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="swagger-ui",
            ),
            path(
                "api/docs/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="docs",
            ),
            path(
                "api/redoc/",
                schema_view.with_ui("redoc", cache_timeout=0),
                name="redoc",
            ),
            path(
                "swagger/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="swagger",
            ),
            path(
                "docs/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="docs-short",
            ),
            path(
                "redoc/",
                schema_view.with_ui("redoc", cache_timeout=0),
                name="redoc-short",
            ),
        ]
else:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="docs",
        ),
        path(
            "api/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        path(
            "swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger",
        ),
        path(
            "docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="docs-short",
        ),
        path(
            "redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc-short",
        ),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

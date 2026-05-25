from importlib import import_module

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse(
        {
            "swagger": "/api/swagger/",
            "schema": "/api/schema/",
            "users": "/api/users/",
            "products": "/api/products/",
            "payments": "/api/payments/",
            "commerce_extras": "/api/commerce-extras/",
        }
    )


def module_available(module_path):
    try:
        import_module(module_path)
    except Exception:
        return False
    return True


def add_include(urlpatterns, prefix, module_path):
    if module_available(module_path):
        urlpatterns.append(path(prefix, include(module_path)))


urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/", api_root, name="api-root-api"),
    path("admin/", admin.site.urls),
]


# User endpoints. These are explicit so Swagger always sees login/register/me.
add_include(urlpatterns, "api/users/", "user.urls")
add_include(urlpatterns, "api/user/", "user.urls")
add_include(urlpatterns, "api/", "user.urls")

# Other project apps.
add_include(urlpatterns, "api/products/", "product.urls")
add_include(urlpatterns, "api/product/", "product.urls")
add_include(urlpatterns, "api/payments/", "payment.urls")
add_include(urlpatterns, "api/payment/", "payment.urls")
add_include(urlpatterns, "api/commerce-extras/", "commerce_extras.urls")
add_include(urlpatterns, "api/commerce_extras/", "commerce_extras.urls")


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

        def swagger_not_installed(request):
            return JsonResponse(
                {
                    "detail": (
                        "Swagger package is not installed. Install drf-spectacular "
                        "or drf-yasg."
                    )
                },
                status=501,
            )

        urlpatterns += [
            path("api/schema/", swagger_not_installed, name="schema"),
            path("api/swagger/", swagger_not_installed, name="swagger-ui"),
            path("api/docs/", swagger_not_installed, name="docs"),
            path("swagger/", swagger_not_installed, name="swagger"),
            path("docs/", swagger_not_installed, name="docs-short"),
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
                "swagger/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="swagger",
            ),
            path(
                "docs/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="docs-short",
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
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

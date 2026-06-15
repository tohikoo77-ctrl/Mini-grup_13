from importlib import import_module

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from commerce_extras.views import HomeKatalogAPIView


def api_root(request):
    return JsonResponse(
        {
            "docs": "/api/docs/",
            "schema": "/api/schema/",
            "users": "/api/users/",
            "products": "/api/products/",
            "categories": "/api/categories/",
            "catalog": "/api/catalog/",
            "carts": "/api/carts/",
            "orders": "/api/orders/",
            "wishlist": "/api/wishlist/",
            "payments": "/api/payments/",
            "commerce_extras": "/api/commerce-extras/",
            "news": "/api/commerce-extras/news/",
            "discounts": "/api/commerce-extras/discounts/",
            "delivery": "/api/delivery/",
            "company": "/api/company/",
            "feedback": "/api/feedback/",
            "contact": "/api/contact/",
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


add_include(urlpatterns, "api/users/", "user.urls")
add_include(urlpatterns, "api/products/", "product.urls")
add_include(urlpatterns, "api/categories/", "category.urls")
add_include(urlpatterns, "api/carts/", "cart.urls")
add_include(urlpatterns, "api/orders/", "order.urls")
add_include(urlpatterns, "api/wishlist/", "commerce_extras.wishlist_urls")
add_include(urlpatterns, "api/payments/", "payment.urls")
add_include(urlpatterns, "api/commerce-extras/", "commerce_extras.urls")
path("api/catalog/", HomeKatalogAPIView.as_view(), name="catalog")
add_include(urlpatterns, "api/delivery/", "delivery.urls")
add_include(urlpatterns, "api/company/", "company.urls")
add_include(urlpatterns, "api/feedback/", "feedback.urls")
add_include(urlpatterns, "api/contact/", "contact.urls")


try:
    from drf_spectacular.views import (
        SpectacularAPIView,
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
            path("api/docs/", swagger_not_installed, name="docs"),
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
                "api/docs/",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="docs",
            ),
        ]
else:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="docs",
        ),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from importlib import import_module

from django.contrib import admin
from django.urls import include, path


def _include_if_available(prefix, module_path):
    try:
        import_module(module_path)
    except Exception:
        return []
    return [path(prefix, include(module_path))]


urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += _include_if_available("api/users/", "apps.user.urls")
urlpatterns += _include_if_available("api/commerce-extras/", "apps.commerce_extras.urls")
urlpatterns += _include_if_available("api/commerce_extras/", "apps.commerce_extras.urls")

from django.apps import AppConfig


class CommerceExtrasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "commerce_extras"

    def ready(self):
        from rest_framework.views import APIView

        from . import views

        for view in vars(views).values():
            if not isinstance(view, type):
                continue

            view_name = view.__name__.lower()
            if ("news" in view_name or "discount" in view_name) and issubclass(view, APIView):
                view.http_method_names = ["get", "head", "options"]
    label = "commerce_extras"
    verbose_name = "Commerce extras"

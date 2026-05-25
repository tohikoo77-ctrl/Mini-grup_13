from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate with username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        login_value = username or kwargs.get(User.USERNAME_FIELD) or kwargs.get("email")
        if login_value is None or password is None:
            return None

        login_value = str(login_value).strip()
        if "@" in login_value and any(
            field.name == "email" for field in User._meta.get_fields()
        ):
            try:
                user = User.objects.get(email__iexact=login_value)
            except User.DoesNotExist:
                return None
            login_value = getattr(user, User.USERNAME_FIELD)

        return super().authenticate(
            request,
            username=login_value,
            password=password,
            **kwargs,
        )

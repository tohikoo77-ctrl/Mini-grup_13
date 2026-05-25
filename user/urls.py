from django.urls import path

from .views import (
    ChangePasswordView,
    ChangeUsernameView,
    LoginView,
    MeView,
    RegisterView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("login", LoginView.as_view(), name="login-no-slash"),
    path("register/", RegisterView.as_view(), name="register"),
    path("register", RegisterView.as_view(), name="register-no-slash"),
    path("me/", MeView.as_view(), name="me"),
    path("me", MeView.as_view(), name="me-no-slash"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("change-password", ChangePasswordView.as_view(), name="change-password-no-slash"),
    path("me/username/", ChangeUsernameView.as_view(), name="user-username"),
    path("me/username", ChangeUsernameView.as_view(), name="user-username-no-slash"),
]

from django.urls import path

from .views import (
    ChangePasswordView,
    ChangeUsernameView,
    ForgotPasswordView,
    LoginView,
    MeView,
    RegisterView,
    ResendCodeView,
    ResetPasswordView,
    VerifyCodeView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("chang e-password/", ChangePasswordView.as_view(), name="change-password"),
    path("me/username/", ChangeUsernameView.as_view(), name="change-username"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("verify/", VerifyCodeView.as_view(), name="verify"),
    path("resend/", ResendCodeView.as_view(), name="resend"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]

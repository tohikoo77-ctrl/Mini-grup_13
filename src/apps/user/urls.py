from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

from apps.user.views import LoginAPIView, SendVerificationCodeAPIView, VerifyEmailCodeAPIView

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="user-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path(
        "verification/send-code/",
        SendVerificationCodeAPIView.as_view(),
        name="user-send-verification-code",
    ),
    path(
        "verification/verify-code/",
        VerifyEmailCodeAPIView.as_view(),
        name="user-verify-email-code",
    ),
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.user.views import (
    SendVerificationCodeAPIView,
    VerifyEmailCodeAPIView,
)

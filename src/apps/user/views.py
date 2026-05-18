from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import get_object_or_404

from apps.user.services import UserService
from .models import User
from .serializer import ResendCodeSerializer, UserSerializer, VerifyCodeSerializer
from .serializer import LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer


class UserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = UserService.create_user(serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserSerializer,
        responses={201: OpenApiResponse(description="Registration successful. Verify your email.")}
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = UserService.create_user(serializer.validated_data)
            return Response({"message": "Registration successful. Verify your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='verify-code')
    def verify_code(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            UserService.verify_user_code(
                serializer.validated_data['email'], 
                serializer.validated_data['code']
            )
            return Response({"message": "Verification successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='resend-code')
    def resend_code(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        if serializer.is_valid():
            UserService.resend_verification_code(serializer.validated_data['email'])
            return Response({"message": "New verification code sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            updated_user = UserService.update_user_profile(user, serializer.validated_data)
            return Response(UserSerializer(updated_user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = UserService.update_user_profile(user, serializer.validated_data)
            return Response(UserSerializer(updated_user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Auth Endpoints ---
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

class LoginView(APIView):
        permission_classes = [AllowAny]
        def post(self, request):
                serializer = LoginSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = UserService.login(
                        serializer.validated_data['email'],
                        serializer.validated_data['password']
                )
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key, "user_id": user.id})


class LogoutView(APIView):
        authentication_classes = [TokenAuthentication]
        def post(self, request):
                request.user.auth_token.delete()
                UserService.logout(request)
                return Response({"message": "Logged out successfully."})


class ForgotPasswordView(APIView):
        permission_classes = [AllowAny]
        def post(self, request):
                serializer = ForgotPasswordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                UserService.send_password_reset_code(serializer.validated_data['email'])
                return Response({"message": "Password reset code sent."})


class ResetPasswordView(APIView):
        permission_classes = [AllowAny]
        def post(self, request):
                serializer = ResetPasswordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                UserService.reset_password(
                        serializer.validated_data['email'],
                        serializer.validated_data['code'],
                        serializer.validated_data['new_password']
                )
                return Response({"message": "Password reset successful."})
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user.serializer import (
    LoginRequestSerializer,
    SendVerificationCodeSerializer,
    VerifyEmailCodeSerializer,
)
from apps.user.swagger import swagger_post

try:
    from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema_view, extend_schema
except ImportError:
    def extend_schema(*args, **kwargs):
        def decorator(obj):
            return obj

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

    class OpenApiTypes:
        INT = int

    class OpenApiParameter:
        PATH = "path"

        def __init__(self, *args, **kwargs):
            pass


class SendVerificationCodeAPIView(generics.GenericAPIView):
    serializer_class = SendVerificationCodeSerializer

    @swagger_post(SendVerificationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Verification code sent to email."},
            status=status.HTTP_200_OK,
        )


class VerifyEmailCodeAPIView(generics.GenericAPIView):
    serializer_class = VerifyEmailCodeSerializer

    @swagger_post(VerifyEmailCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


try:
    from rest_framework_simplejwt.views import TokenObtainPairView
except ImportError:
    TokenObtainPairView = None


if TokenObtainPairView is not None:
    class LoginAPIView(TokenObtainPairView):
        @swagger_post(LoginRequestSerializer)
        def post(self, request, *args, **kwargs):
            return super().post(request, *args, **kwargs)


try:
    from django.contrib.auth import get_user_model

    UserViewSet.queryset = get_user_model().objects.all()
    UserViewSet = extend_schema_view(
        list=extend_schema(operation_id="users_users_list"),
        retrieve=extend_schema(
            operation_id="users_users_retrieve_detail",
            parameters=[
                OpenApiParameter(
                    name="id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                )
            ],
        ),
    )(UserViewSet)
except NameError:
    pass

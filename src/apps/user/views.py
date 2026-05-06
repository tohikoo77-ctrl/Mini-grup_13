from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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

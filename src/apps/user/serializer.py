from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import User
from rest_framework.exceptions import ValidationError
from .utils import is_uzbek_phone_valid

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'address', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone_number(self, value):
        if value and not is_uzbek_phone_valid(value):
            raise ValidationError("Phone number must be in the format: '+998XXXXXXXXX'.")
        return value

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# Forgot Password (Send Code) Serializer
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

# Reset Password Serializer
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.user.models import EmailVerificationCode, send_user_verification_code


class SendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self, **kwargs):
        User = get_user_model()
        user = User.objects.get(email=self.validated_data["email"])
        send_user_verification_code(user)
        return user


class VerifyEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        verification = (
            EmailVerificationCode.objects.filter(
                email=attrs["email"],
                code=attrs["code"],
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )
        if verification is None:
            raise serializers.ValidationError("Invalid verification code.")

        attrs["verification"] = verification
        return attrs

    def save(self, **kwargs):
        verification = self.validated_data["verification"]
        verification.is_used = True
        verification.save(update_fields=["is_used"])

        user = verification.user
        if hasattr(user, "is_verified"):
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        return user


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("username"):
            raise serializers.ValidationError("Email or username is required.")
        return attrs

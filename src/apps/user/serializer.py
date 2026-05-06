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
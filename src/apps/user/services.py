import random
from datetime import timedelta
from typing import Any, Dict
from django.db import transaction


from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import User



class UserService:
    @staticmethod
    def login(email: str, password: str) -> User:
        from django.contrib.auth import authenticate
        user = authenticate(email=email, password=password)
        if user is None:
            raise ValidationError({"detail": "Invalid email or password."})
        if not user.is_active:
            raise ValidationError({"detail": "User account is not active."})
        return user

    @staticmethod
    def logout(request) -> None:
        from django.contrib.auth import logout
        logout(request)

    @staticmethod
    def send_password_reset_code(email: str) -> None:
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError({"email": "User not found."})
        code = UserService._generate_verification_code(user)
        print(f"PASSWORD RESET CODE for {user.email}: {code}")

    @staticmethod
    def reset_password(email: str, code: str, new_password: str) -> None:
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError({"email": "User not found."})
        if user.verification_code != code:
            raise ValidationError({"code": "Invalid code."})
        if timezone.now() > user.verification_code_expires_at:
            raise ValidationError({"code": "Code expired."})
        user.set_password(new_password)
        user.verification_code = None
        user.verification_code_expires_at = None
        user.save()

    @staticmethod
    def _generate_verification_code(user:  User) -> str:
     
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.verification_code_expires_at = timezone.now() + timedelta(minutes=10)
        user.save()
        return code

    @staticmethod
    @transaction.atomic
    def create_user(data: Dict[str, Any]) ->   User:
       
        password = data.pop('password')
        user = User.objects.create_user(
            password=password,
            is_active=False,
            **data
        )
        code = UserService._generate_verification_code(user)
      
        print(f"VERIFICATION CODE for {user.email}: {code}")
        return user

    @staticmethod
    @transaction.atomic
    def verify_user_code(email: str, code: str) -> User:
        """Verifies the code and activates the user."""
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError({"email": "User not found."})

        if user.is_active:
            raise ValidationError({"email": "User is already verified."})

        if user.verification_code != code:
            raise ValidationError({"code": "Invalid verification code."})

        if timezone.now() > user.verification_code_expires_at:
            raise ValidationError({"code": "Code expired."})

        user.is_active = True
        user.verification_code = None
        user.verification_code_expires_at = None
        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def resend_verification_code(email: str) -> None:
        """Generates and sends a new code for inactive users."""
        user = User.objects.filter(email=email).first()
        if not user or user.is_active:
            raise ValidationError({"email": "Cannot resend code to this user."})

        code = UserService._generate_verification_code(user)
        print(f"RESENT CODE for {user.email}: {code}")

    @staticmethod
    @transaction.atomic
    def update_user_profile(user: User, data: Dict[str, Any]) -> User:
        """
        Updates an existing user's attributes.
        Handles password hashing if a new password is provided.
        """
        password = data.pop('password', None)
        if password:
            user.set_password(password)

        for attr, value in data.items():
            setattr(user, attr, value)

        user.save()
        return user
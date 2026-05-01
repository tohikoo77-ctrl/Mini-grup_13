import random
from datetime import timedelta
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Any, Dict
from django.utils import timezone
from rest_framework.exceptions import ValidationError

User = get_user_model()

class UserService:
    """
    Service layer to handle business logic for the User model.
    Encapsulates database operations and logic to keep views and serializers clean.
    """

    @staticmethod
    def _generate_verification_code(user: User) -> str:
        """Generates a 6-digit code and sets a 10-minute expiration."""
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.verification_code_expires_at = timezone.now() + timedelta(minutes=10)
        user.save()
        return code

    @staticmethod
    @transaction.atomic
    def create_user(data: Dict[str, Any]) -> User:
        """
        Creates a new user instance.
        Uses the create_user manager method to handle password hashing automatically.
        Sets user to inactive until verified.
        """
        password = data.pop('password')
        user = User.objects.create_user(
            password=password,
            is_active=False,
            **data
        )
        code = UserService._generate_verification_code(user)
        # Replace with actual email/SMS sending logic in production
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
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Any, Dict

User = get_user_model()

class UserService:
    """
    Service layer to handle business logic for the User model.
    Encapsulates database operations and logic to keep views and serializers clean.
    """

    @staticmethod
    @transaction.atomic
    def create_user(data: Dict[str, Any]) -> User:
        """
        Creates a new user instance.
        Uses the create_user manager method to handle password hashing automatically.
        """
        password = data.pop('password')
        user = User.objects.create_user(
            password=password,
            **data
        )
        return user

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
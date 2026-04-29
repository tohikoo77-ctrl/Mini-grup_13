from rest_framework.serializers import ModelSerializer
from .models import User
from rest_framework.exceptions import ValidationError
from .utils import is_uzbek_phone_valid

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def validate_phone_number(self, value):
        if value and not is_uzbek_phone_valid(value):
            raise ValidationError("Phone number must be in the format: '+998XXXXXXXXX'.")
        return value
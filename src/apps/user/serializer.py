from rest_framework.serializers import ModelSerializer
from .models import User
from rest_framework.exceptions import ValidationError

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


def validate_phone_number(self, value):
        if not value.startswith('+998'):
            raise ValidationError("+998 bilan boshlanishi shart")
        return value
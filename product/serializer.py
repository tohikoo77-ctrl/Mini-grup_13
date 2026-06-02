from rest_framework.serializers import ModelSerializer
from .models import Product
from category.serializers import CategorySerializer

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductFullSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
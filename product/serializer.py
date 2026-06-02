from decimal import Decimal, InvalidOperation

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Product
from category.serializers import CategorySerializer


def _to_decimal(value):
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


class ProductSerializer(ModelSerializer):
    has_discount = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    @extend_schema_field(bool)
    def get_has_discount(self, obj):
        return bool(getattr(obj, "discount_percent", 0))

    @extend_schema_field(serializers.DecimalField(max_digits=18, decimal_places=2))
    def get_discounted_price(self, obj):
        price = _to_decimal(getattr(obj, "price", None))
        percent = getattr(obj, "discount_percent", 0) or 0
        if price is None or percent <= 0:
            return None
        discounted = price * (Decimal(100) - Decimal(percent)) / Decimal(100)
        return f"{discounted.quantize(Decimal('0.01'))}"


class ProductFullSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    has_discount = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    @extend_schema_field(bool)
    def get_has_discount(self, obj):
        return bool(getattr(obj, "discount_percent", 0))

    @extend_schema_field(serializers.DecimalField(max_digits=18, decimal_places=2))
    def get_discounted_price(self, obj):
        price = _to_decimal(getattr(obj, "price", None))
        percent = getattr(obj, "discount_percent", 0) or 0
        if price is None or percent <= 0:
            return None
        discounted = price * (Decimal(100) - Decimal(percent)) / Decimal(100)
        return f"{discounted.quantize(Decimal('0.01'))}"
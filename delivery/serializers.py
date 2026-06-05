from rest_framework import serializers
from .models import ShippingMethod, OrderTracking


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'price', 'delivery_days', 'is_active']


class OrderTrackingSerializer(serializers.ModelSerializer):
    shipping_method = ShippingMethodSerializer(read_only=True)

    class Meta:
        model = OrderTracking
        fields = [
            'id', 'order', 'shipping_method', 'status', 'tracking_number',
            'current_location', 'shipped_date', 'estimated_delivery',
            'delivered_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'order']

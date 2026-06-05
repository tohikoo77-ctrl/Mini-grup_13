from rest_framework import serializers
from .models import Order, OrderItem, ReturnRequest


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_image',
            'quantity',
            'price',
            'total_price'
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_username',
            'items',
            'total_price',
            'status',
            'created_at'
        ]
        read_only_fields = ['total_price', 'created_at']


class ReturnRequestSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_item_id = serializers.IntegerField(source='order_item.id', read_only=True)
    product_name = serializers.CharField(source='order_item.product.name', read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            'id', 'order', 'order_id', 'order_item', 'order_item_id', 'product_name',
            'reason', 'description', 'status', 'admin_notes',
            'return_shipping_cost', 'refund_amount',
            'requested_at', 'approved_at', 'received_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'admin_notes', 'return_shipping_cost', 'refund_amount',
            'approved_at', 'received_at', 'completed_at', 'requested_at'
        ]
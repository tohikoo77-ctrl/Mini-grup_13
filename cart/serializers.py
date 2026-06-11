from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Cart, CartItem

class CartItemSerializer(ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), required=False)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']  



class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
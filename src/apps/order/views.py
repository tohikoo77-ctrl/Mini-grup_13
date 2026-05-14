from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.product.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
        order = self.get_object()

        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only modify your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():

            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            product = Product.objects.get(id=product.id)

            if product.stock < quantity:
                return Response(
                    {"error": f"Insufficient stock. Available: {product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            existing_item = OrderItem.objects.filter(
                order=order,
                product=product
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
                order.update_total_price()
                return Response(OrderItemSerializer(existing_item).data)

            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=int(product.price)
            )

            order.update_total_price()
            return Response(OrderItemSerializer(item).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-item/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        order = self.get_object()

        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only modify your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )

        item = get_object_or_404(OrderItem, id=item_id, order=order)
        item.delete()
        order.update_total_price()

        return Response({"message": "Item removed successfully"})


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
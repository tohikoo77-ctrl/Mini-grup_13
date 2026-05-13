from drf_spectacular.utils import extend_schema, OpenApiResponse
    @extend_schema(request=OrderSerializer, responses={201: OpenApiResponse(description="Order created.")})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.product.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        """Set the user when creating an order"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
        """Add an item to an order"""
        order = self.get_object()

        # Check if order belongs to current user or user is staff
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only modify your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            quantity = serializer.validated_data['quantity']

            # Check if product exists and has enough stock
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if product.stock < quantity:
                return Response(
                    {"error": f"Insufficient stock. Available: {product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if item already exists in order
            existing_item = OrderItem.objects.filter(order=order, product=product).first()
            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
                order.update_total_price()
                return Response(OrderItemSerializer(existing_item).data)

            # Create new item
            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=int(product.price)  # Convert to int if needed
            )
            order.update_total_price()
            return Response(OrderItemSerializer(item).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-item/(?P<item_id>\d+)')
    def remove_item(self, request, pk=None, item_id=None):
        """Remove an item from an order"""
        order = self.get_object()

        # Check if order belongs to current user or user is staff
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only modify your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            item = OrderItem.objects.get(id=item_id, order=order)
            item.delete()
            order.update_total_price()
            return Response({"message": "Item removed successfully"})
        except OrderItem.DoesNotExist:
            return Response(
                {"error": "Item not found in this order"},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

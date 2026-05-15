from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.product.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @extend_schema(
        request=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
       
        serializer.save(user=self.request.user)

    @extend_schema(
        request=OrderItemSerializer,
        responses={
            201: OrderItemSerializer,
            200: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error or insufficient stock."),
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Product not found."),
        },
    )
    @action(detail=True, methods=["post"], url_path="add-item")
    def add_item(self, request, pk=None):
        """Add an item to an order."""
        order = self.get_object()

        # Only the owner or staff can modify the order.
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only modify your own orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data["product"]
            quantity = serializer.validated_data["quantity"]

            # Double-check stock. Trust, but verify, because databases are sneaky.
            if product.stock < quantity:
                return Response(
                    {"error": f"Insufficient stock. Available: {product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If the product already exists in the order, increase quantity.
            existing_item = OrderItem.objects.filter(
                order=order,
                product=product
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                existing_item.price = product.price
                existing_item.save()
                order.update_total_price()
                return Response(
                    OrderItemSerializer(existing_item).data,
                    status=status.HTTP_200_OK,
                )

            # Otherwise, create a new order item.
            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            order.update_total_price()

            return Response(
                OrderItemSerializer(item).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Item removed successfully."),
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Item not found in this order."),
        },
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path=r"remove-item/(?P<item_id>\d+)",
    )
    def remove_item(self, request, pk=None, item_id=None):
        """Remove an item from an order."""
        order = self.get_object()

        # Only the owner or staff can modify the order.
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only modify your own orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            item = OrderItem.objects.get(id=item_id, order=order)
            item.delete()
            order.update_total_price()

            return Response(
                {"message": "Item removed successfully"},
                status=status.HTTP_200_OK,
            )
        except OrderItem.DoesNotExist:
            return Response(
                {"error": "Item not found in this order"},
                status=status.HTTP_404_NOT_FOUND,
            )


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    @extend_schema(
        request=OrderItemSerializer,
        responses={
            201: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=OrderItemSerializer,
        responses={
            200: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=OrderItemSerializer,
        responses={
            200: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Order item deleted."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

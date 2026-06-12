from decimal import Decimal

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderItem, ReturnRequest
from .serializers import OrderSerializer, OrderItemSerializer, ReturnRequestSerializer
from product.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @extend_schema(
        tags=["Orders"],
        request=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)

        if not self.request.user.is_authenticated:
            return

        try:
            cart = Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            return

        cart_items = cart.items.select_related('product')
        if not cart_items.exists():
            return

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=Decimal(cart_item.product.price),
            )

        order.update_total_price()
        cart_items.delete()

    @extend_schema(
        tags=["Orders"],
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
        tags=["Orders"],
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
        tags=["Orders"],
        request=OrderItemSerializer,
        responses={
            201: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Orders"],
        request=OrderItemSerializer,
        responses={
            200: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Orders"],
        request=OrderItemSerializer,
        responses={
            200: OrderItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Orders"],
        responses={
            204: OpenApiResponse(description="Order item deleted."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ReturnRequestViewSet(viewsets.ModelViewSet):
    """Manage return requests for orders"""
    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users see only their own return requests"""
        if self.request.user.is_staff:
            return ReturnRequest.objects.all()
        return ReturnRequest.objects.filter(order__user=self.request.user)

    def perform_create(self, serializer):
        """Ensure return request belongs to user's order"""
        order_id = self.request.data.get('order')
        order_item_id = self.request.data.get('order_item')
        
        try:
            order = Order.objects.get(id=order_id, user=self.request.user)
            order_item = OrderItem.objects.get(id=order_item_id, order=order)
            
            # Check if return already exists for this item
            if ReturnRequest.objects.filter(order_item=order_item).exists():
                raise serializers.ValidationError("A return request already exists for this item")
            
            serializer.save()
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        except OrderItem.DoesNotExist:
            raise serializers.ValidationError("Order item not found")

    @action(detail=False, methods=['get'])
    def my_returns(self, request):
        """Get user's return requests"""
        returns = ReturnRequest.objects.filter(order__user=request.user)
        serializer = self.get_serializer(returns, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve return request (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Only admin can approve returns'}, status=status.HTTP_403_FORBIDDEN)
        
        ret = self.get_object()
        ret.status = 'approved'
        ret.admin_notes = request.data.get('notes', '')
        ret.save()
        serializer = self.get_serializer(ret)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject return request (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Only admin can reject returns'}, status=status.HTTP_403_FORBIDDEN)
        
        ret = self.get_object()
        ret.status = 'rejected'
        ret.admin_notes = request.data.get('notes', '')
        ret.save()
        serializer = self.get_serializer(ret)
        return Response(serializer.data)

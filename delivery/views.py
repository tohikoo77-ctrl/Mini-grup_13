from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ShippingMethod, OrderTracking
from .serializers import ShippingMethodSerializer, OrderTrackingSerializer


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """Get available shipping methods"""
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = []


class OrderTrackingViewSet(viewsets.GenericViewSet):
    """Track order delivery"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderTrackingSerializer
    queryset = OrderTracking.objects.all()
    lookup_field = 'order_id'

    def retrieve(self, request, *args, **kwargs):
        """Get tracking info for specific order (lookup by `order_id`).

        Use `self.get_object()` so DRF resolves the lookup field (`order_id`) from
        `self.kwargs` regardless of the parameter name passed to this method.
        """
        try:
            tracking = self.get_object()
            serializer = self.get_serializer(tracking)
            return Response(serializer.data)
        except Exception:
            return Response({'error': 'Tracking not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_orders(self, request):
        """Get tracking info for user's orders"""
        from order.models import Order
        orders = Order.objects.filter(user=request.user)
        trackings = OrderTracking.objects.filter(order__in=orders)
        serializer = self.get_serializer(trackings, many=True)
        return Response(serializer.data)

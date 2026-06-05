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


class OrderTrackingViewSet(viewsets.ViewSet):
    """Track order delivery"""
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """Get tracking info for specific order"""
        try:
            tracking = OrderTracking.objects.get(order_id=pk)
            serializer = OrderTrackingSerializer(tracking)
            return Response(serializer.data)
        except OrderTracking.DoesNotExist:
            return Response({'error': 'Tracking not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get tracking info for user's orders"""
        from order.models import Order
        orders = Order.objects.filter(user=request.user)
        trackings = OrderTracking.objects.filter(order__in=orders)
        serializer = OrderTrackingSerializer(trackings, many=True)
        return Response(serializer.data)

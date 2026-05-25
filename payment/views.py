from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Payment
from .serializers import PaymentSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order__id', 'method', 'status']
    ordering_fields = ['amount', 'created_at', 'status']

    @extend_schema(request=PaymentSerializer, responses={201: OpenApiResponse(description="Payment created.")})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(request=PaymentSerializer, responses={200: PaymentSerializer})
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @extend_schema(request=PaymentSerializer, responses={200: PaymentSerializer})
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(responses={204: OpenApiResponse(description="Payment deleted.")})
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """List pending payments"""
        payments = Payment.objects.filter(status=Payment.Status.PENDING)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='completed')
    def completed(self, request):
        """List completed payments"""
        payments = Payment.objects.filter(status=Payment.Status.COMPLETED)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

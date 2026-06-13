from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema

from .models import FAQ
from .serializers import FAQSerializer


@extend_schema(
    summary="List FAQs",
    description="Returns a list of active frequently asked questions for the FAQ page.",
)
class FAQListAPIView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True).order_by("order")
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]

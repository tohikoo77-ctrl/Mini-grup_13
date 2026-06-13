from rest_framework import generics, permissions
from .models import FAQ
from .serializers import FAQSerializer


class FAQListAPIView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True).order_by("order")
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]

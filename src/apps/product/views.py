from rest_framework import viewsets
from .models import Product
from .serializer import ProductSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer

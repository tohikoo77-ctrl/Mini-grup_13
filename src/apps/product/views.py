from drf_spectacular.utils import extend_schema, OpenApiResponse
	@extend_schema(request=ProductSerializer, responses={201: OpenApiResponse(description="Product created.")})
	def create(self, request, *args, **kwargs):
		return super().create(request, *args, **kwargs)
from rest_framework import viewsets
from .models import Product
from .serializer import ProductSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer

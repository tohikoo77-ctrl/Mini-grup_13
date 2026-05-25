from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product
from .serializer import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
   
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['name', 'description', 'category__name']
	ordering_fields = ['price', 'created_at', 'updated_at']
  
	
	@extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer)
		return Response(serializer.data)

	@extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
	def partial_update(self, request, *args, **kwargs):
		kwargs['partial'] = True
		return self.update(request, *args, **kwargs)

	@extend_schema(responses={204: OpenApiResponse(description="Product deleted.")})
	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		self.perform_destroy(instance)
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=False, methods=['get'], url_path='hits')
	def hits(self, request):
		"""List hit products"""
		products = Product.objects.filter(is_hit=True)
		serializer = self.get_serializer(products, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'], url_path='new')
	def new(self, request):
		"""List new products"""
		products = Product.objects.filter(is_new=True)
		serializer = self.get_serializer(products, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'], url_path='sale')
	def sale(self, request):
		"""List products on sale"""
		products = Product.objects.filter(is_sale=True)
		serializer = self.get_serializer(products, many=True)
		return Response(serializer.data)

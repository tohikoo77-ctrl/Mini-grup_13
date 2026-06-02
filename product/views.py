from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Product
from .serializer import ProductFullSerializer, ProductSerializer


class ProductPagePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "created_at", "updated_at"]

    @extend_schema(request=ProductSerializer, responses={201: ProductSerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(responses={200: ProductSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(responses={200: ProductSerializer})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(responses={204: OpenApiResponse(description="Product deleted.")})
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={200: ProductSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="hits")
    def hits(self, request):
        products = Product.objects.filter(is_hit=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(responses={200: ProductSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="new")
    def new(self, request):
        products = Product.objects.filter(is_new=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(responses={200: ProductSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="sale")
    def sale(self, request):
        products = Product.objects.filter(is_sale=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page", required=False, type=int),
            OpenApiParameter(name="page_size", required=False, type=int),
            OpenApiParameter(
                name="search",
                required=False,
                type=str,
                description="Search in name, description, category name.",
            ),
            OpenApiParameter(
                name="ordering",
                required=False,
                type=str,
                description="Ordering fields: price, created_at, updated_at. Use -field for desc.",
            ),
        ],
        responses={200: ProductFullSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        queryset = self.filter_queryset(self.get_queryset().select_related("category"))
        page = self.paginate_queryset(queryset)
        serializer = ProductFullSerializer(
            page if page is not None else queryset,
            many=True,
            context=self.get_serializer_context(),
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @extend_schema(responses={200: ProductFullSerializer})
    @action(detail=True, methods=["get"], url_path="full")
    def full_detail(self, request, pk=None):
        product = self.get_object()
        serializer = ProductFullSerializer(product, context=self.get_serializer_context())
        return Response(serializer.data)

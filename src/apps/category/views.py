from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ViewSet):
    """
    Manual CRUD ViewSet for Category.
    Because apparently even categories need full bureaucratic processing.
    """

    @extend_schema(
        responses=CategorySerializer(many=True)
    )
    def list(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: CategorySerializer,
            404: OpenApiResponse(description="Category not found."),
        },
    )
    def retrieve(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Category not found."),
        },
    )
    def update(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Category not found."),
        },
    )
    def partial_update(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Category deleted successfully."),
            404: OpenApiResponse(description="Category not found."),
        },
    )
    def destroy(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
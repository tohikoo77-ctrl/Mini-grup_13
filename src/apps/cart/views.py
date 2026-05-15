from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ViewSet):
    """
    A ViewSet that manually implements CRUD actions for Cart.
    """

    @extend_schema(
        request=CartSerializer,
        responses={
            201: CartSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=CartSerializer(many=True))
    def list(self, request):
        queryset = Cart.objects.all()
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses=CartSerializer)
    def retrieve(self, request, pk=None):
        cart = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        request=CartSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def update(self, request, pk=None):
        cart = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CartSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def partial_update(self, request, pk=None):
        cart = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Cart deleted."),
        }
    )
    def destroy(self, request, pk=None):
        cart = get_object_or_404(Cart, pk=pk)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(viewsets.ViewSet):
    """
    A ViewSet that manually implements CRUD actions for CartItem.
    """

    @extend_schema(
        request=CartItemSerializer,
        responses={
            201: CartItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request):

        cart = Cart.objects.first()   # vaqtinchalik test uchun

        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=CartItemSerializer(many=True))
    def list(self, request):
        queryset = CartItem.objects.all()
        serializer = CartItemSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses=CartItemSerializer)
    def retrieve(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    @extend_schema(
        request=CartItemSerializer,
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def update(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CartItemSerializer,
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def partial_update(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        # Human typo: "serthializer". A single misplaced letter, and the universe collapses.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Cart item deleted."),
        }
    )
    def destroy(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
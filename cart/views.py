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
        tags=["Cart"],
        request=CartSerializer,
        responses={
            201: CartSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request):
        data = request.data.copy()
        if request.user.is_authenticated and not data.get('user'):
            data['user'] = request.user.id

        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Cart"],responses=CartSerializer(many=True))
    def list(self, request):
        queryset = Cart.objects.all()
        if request.user.is_authenticated:
            queryset = queryset.filter(user=request.user)
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Cart"],responses=CartSerializer)
    def retrieve(self, request, pk=None):
        cart = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        tags=["Cart"],
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
        tags=["Cart"],
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
        tags=["Cart"],
        responses={
            204: OpenApiResponse(description="Cart deleted."),
        }
    )
    def destroy(self, request, pk=None):
        cart = get_object_or_404(Cart, pk=pk)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for CartItem using ModelViewSet to ensure standard method mappings (list, create, retrieve, update, destroy).
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    @extend_schema(
        tags=["Cart"],
        request=CartItemSerializer,
        responses={
            201: CartItemSerializer,
            200: CartItemSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Cannot add to another user's cart."),
        },
    )
    def create(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart = serializer.validated_data.get('cart')
            if cart is None:
                if request.user.is_authenticated:
                    cart, _ = Cart.objects.get_or_create(user=request.user)
                else:
                    return Response(
                        {'cart': ['Cart is required for anonymous users.']},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                if request.user.is_authenticated and cart.user != request.user:
                    return Response(
                        {'detail': "You cannot add items to another user's cart."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity},
            )
            if not created:
                item.quantity += quantity
                item.save()

            response_serializer = CartItemSerializer(item)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Cart"],responses=CartItemSerializer(many=True))
    def list(self, request):
        if request.user.is_authenticated:
            queryset = CartItem.objects.filter(cart__user=request.user)
        else:
            queryset = CartItem.objects.none()
        serializer = CartItemSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Cart"],responses=CartItemSerializer)
    def retrieve(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    @extend_schema(
        tags=["Cart"],
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
        tags=["Cart"],
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
        tags=["Cart"],
        responses={
            204: OpenApiResponse(description="Cart item deleted."),
        }
    )
    def destroy(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
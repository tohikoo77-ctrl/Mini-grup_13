from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WishlistItem
from .serializers import WishlistItemSerializer, WishlistToggleSerializer, get_product_model


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["Wishlist"],
        summary="List wishlist",
        description="Returns products saved in the current user's wishlist.",
        responses={200: WishlistItemSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Wishlist"],
        summary="Get wishlist item",
        description="Returns one wishlist item owned by the current user.",
        responses={
            200: WishlistItemSerializer,
            404: OpenApiResponse(description="Wishlist item not found."),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Wishlist"],
        summary="Add product to wishlist",
        description="Adds a product to the current user's wishlist.",
        request=WishlistItemSerializer,
        responses={
            201: WishlistItemSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Wishlist"],
        summary="Replace wishlist item",
        description="Replaces the product stored in one wishlist item owned by the current user.",
        request=WishlistItemSerializer,
        responses={
            200: WishlistItemSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Wishlist item not found."),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Wishlist"],
        summary="Update wishlist item",
        description="Partially updates one wishlist item owned by the current user.",
        request=WishlistItemSerializer,
        responses={
            200: WishlistItemSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Wishlist item not found."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Wishlist"],
        summary="Remove wishlist item",
        description="Removes a product from the current user's wishlist.",
        responses={
            204: OpenApiResponse(description="Wishlist item removed."),
            404: OpenApiResponse(description="Wishlist item not found."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["Wishlist"],
        summary="Toggle wishlist product",
        description="Adds the product if it is not saved; removes it if it already exists.",
        request=WishlistToggleSerializer,
        responses={
            200: OpenApiResponse(description="Product removed from wishlist."),
            201: WishlistItemSerializer,
            404: OpenApiResponse(description="Product not found."),
        },
    )
    @action(detail=False, methods=["post"])
    def toggle(self, request):
        input_serializer = WishlistToggleSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        product_id = input_serializer.validated_data["product_id"]

        product_model = get_product_model()
        try:
            product = product_model.objects.get(pk=product_id)
        except product_model.DoesNotExist:
            return Response({"product_id": ["Product not found."]}, status=status.HTTP_404_NOT_FOUND)

        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            item.delete()
            return Response({"in_wishlist": False}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(item)
        return Response(
            {"in_wishlist": True, "item": serializer.data},
            status=status.HTTP_201_CREATED,
        )

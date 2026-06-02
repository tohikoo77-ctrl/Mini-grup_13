from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Discount
from .serializers import DiscountSerializer


class DiscountViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = DiscountSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve", "active"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = Discount.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.active()
        return queryset.prefetch_related("products")

    @extend_schema(
        tags=["Discounts"],
        summary="List active discounts",
        description=(
            "Returns active discounts for public users (published and within start/end date). "
            "Staff users can see all discounts."
        ),
        responses={200: DiscountSerializer(many=True)},
        auth=[],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Discounts"],
        summary="List active discounts",
        description="Returns currently active discounts (published and within start/end date).",
        responses={200: DiscountSerializer(many=True)},
        auth=[],
    )
    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        queryset = self.filter_queryset(Discount.objects.active().prefetch_related("products"))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Discounts"],
        summary="Get discount detail",
        description="Returns one discount item by slug.",
        responses={
            200: DiscountSerializer,
            404: OpenApiResponse(description="Discount not found."),
        },
        auth=[],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Discounts"],
        summary="Replace discount",
        description="Admin-only endpoint for replacing a discount item.",
        request=DiscountSerializer,
        responses={
            200: DiscountSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Admin access required."),
            404: OpenApiResponse(description="Discount not found."),
        },
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @extend_schema(
        tags=["Discounts"],
        summary="Update discount",
        description="Admin-only endpoint for partially updating a discount item.",
        request=DiscountSerializer,
        responses={
            200: DiscountSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Admin access required."),
            404: OpenApiResponse(description="Discount not found."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["Discounts"],
        summary="Delete discount",
        description="Admin-only endpoint for deleting a discount item.",
        responses={
            204: OpenApiResponse(description="Discount deleted."),
            403: OpenApiResponse(description="Admin access required."),
            404: OpenApiResponse(description="Discount not found."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


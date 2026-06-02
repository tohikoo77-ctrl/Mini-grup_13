from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import News
from .serializers import NewsSerializer


class NewsViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NewsSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = News.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.daily()
        return queryset

    @extend_schema(
        tags=["News"],
        summary="Create news",
        description="Admin-only endpoint for creating a news item.",
        request=NewsSerializer,
        responses={
            201: NewsSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Admin access required."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["News"],
        summary="List published news",
        description=(
            "Returns published news from the last 24 hours for public users. "
            "Staff users can see all news."
        ),
        responses={200: NewsSerializer(many=True)},
        auth=[],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["News"],
        summary="List daily news",
        description="Returns published news items published within the last 24 hours.",
        responses={200: NewsSerializer(many=True)},
        auth=[],
    )
    @action(detail=False, methods=["get"], url_path="daily")
    def daily(self, request):
        queryset = self.filter_queryset(News.objects.daily())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["News"],
        summary="Get news detail",
        description="Returns one news item by slug.",
        responses={
            200: NewsSerializer,
            404: OpenApiResponse(description="News not found."),
        },
        auth=[],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["News"],
        summary="Replace news",
        description="Admin-only endpoint for replacing a news item.",
        request=NewsSerializer,
        responses={
            200: NewsSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Admin access required."),
            404: OpenApiResponse(description="News not found."),
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
        tags=["News"],
        summary="Update news",
        description="Admin-only endpoint for partially updating a news item.",
        request=NewsSerializer,
        responses={
            200: NewsSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Admin access required."),
            404: OpenApiResponse(description="News not found."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["News"],
        summary="Delete news",
        description="Admin-only endpoint for deleting a news item.",
        responses={
            204: OpenApiResponse(description="News deleted."),
            403: OpenApiResponse(description="Admin access required."),
            404: OpenApiResponse(description="News not found."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

from datetime import timedelta

from django.db.models import Avg, Count, F, Q
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

try:
    from drf_yasg import openapi
    from drf_yasg.utils import swagger_auto_schema
except Exception:
    openapi = None

    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

from .models import News, OrderAddress, OrderReview, ProductComparison, WishlistItem
from .serializers import (
    ChangePasswordSerializer,
    ChangeUsernameSerializer,
    NewsSerializer,
    OrderAddressSerializer,
    OrderReviewSerializer,
    ProductCompareRequestSerializer,
    ProductComparisonSerializer,
    UserProfileSerializer,
    WishlistToggleSerializer,
    WishlistItemSerializer,
    get_order_model,
    get_product_model,
    serialize_order,
    serialize_product,
)


def _model_field_names(model):
    return {field.name for field in model._meta.fields}


def _relation_field_names(model):
    if model is None:
        return set()
    return {
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "is_relation", False)
    }


def _param(name, description, param_type="string"):
    if openapi is None:
        return None
    return openapi.Parameter(
        name,
        openapi.IN_QUERY,
        description=description,
        type=param_type,
    )


def _schema(properties, required=None):
    if openapi is None:
        return None
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties,
        required=required or [],
    )


def _array_schema(item_schema):
    if openapi is None:
        return None
    return openapi.Schema(type=openapi.TYPE_ARRAY, items=item_schema)


def _positive_int(value, default, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    parsed = max(parsed, 1)
    if maximum is not None:
        parsed = min(parsed, maximum)
    return parsed


PRODUCT_FILTER_PARAMS = (
    []
    if openapi is None
    else [
        _param("search", "Search in name, title, description, short_description, sku"),
        _param("category", "Category id, slug, or name"),
        _param("brand", "Brand id, slug, or name"),
        _param("color", "Color id, slug, or name"),
        _param("size", "Size id, slug, or name"),
        _param("min_price", "Minimum price", "number"),
        _param("max_price", "Maximum price", "number"),
        _param("in_stock", "true/false"),
        _param("has_discount", "true/false"),
        _param("is_new", "true/false"),
        _param("popular", "true/false"),
        _param("ordering", "price, -price, name, -name, created_at, -created_at, popularity, -popularity"),
        _param("page", "Page number", "integer"),
        _param("page_size", "Items per page, max 100", "integer"),
    ]
)

HOME_PARAMS = [] if openapi is None else [_param("limit", "Popular products limit, max 50", "integer")]
ORDER_REVIEW_PARAMS = [] if openapi is None else [_param("order", "Filter reviews by order id", "integer")]

PRODUCT_OBJECT_SCHEMA = (
    None
    if openapi is None
    else openapi.Schema(
        type=openapi.TYPE_OBJECT,
        description="Product object. Exact fields come from your ProductSerializer/Product model.",
        additional_properties=True,
    )
)
ORDER_OBJECT_SCHEMA = (
    None
    if openapi is None
    else openapi.Schema(
        type=openapi.TYPE_OBJECT,
        description="Order object. Exact fields come from your OrderSerializer/Order model.",
        additional_properties=True,
    )
)
PRODUCT_DISCOVERY_RESPONSE = (
    None
    if openapi is None
    else _schema(
        {
            "count": openapi.Schema(type=openapi.TYPE_INTEGER),
            "page": openapi.Schema(type=openapi.TYPE_INTEGER),
            "page_size": openapi.Schema(type=openapi.TYPE_INTEGER),
            "results": _array_schema(PRODUCT_OBJECT_SCHEMA),
        }
    )
)
PRODUCT_COMPARE_RESPONSE = (
    None
    if openapi is None
    else _schema(
        {
            "products": _array_schema(PRODUCT_OBJECT_SCHEMA),
            "comparison": _array_schema(
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "product_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "cost": openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True),
                        "stock": openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True),
                        "review": openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True),
                    },
                )
            ),
            "comparable_fields": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
        }
    )
)
HOME_RESPONSE = (
    None
    if openapi is None
    else _schema(
        {
            "popular_products": _array_schema(PRODUCT_OBJECT_SCHEMA),
            "latest_news": _array_schema(
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Latest published news items.",
                    additional_properties=True,
                )
            ),
        }
    )
)
PASSWORD_RESPONSE = (
    None
    if openapi is None
    else _schema({"detail": openapi.Schema(type=openapi.TYPE_STRING)})
)
USERNAME_RESPONSE = (
    None
    if openapi is None
    else _schema(
        {
            "detail": openapi.Schema(type=openapi.TYPE_STRING),
            "username": openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)
WISHLIST_TOGGLE_RESPONSE = (
    None
    if openapi is None
    else _schema(
        {
            "in_wishlist": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            "item": openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True),
        }
    )
)


class NewsWritePermissionMixin:
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["News"],
        operation_summary="List published news",
        operation_description="Returns published news for public users. Staff users can see all news.",
        responses={200: NewsSerializer(many=True)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["News"],
        operation_summary="Get news detail",
        operation_description="Returns one news item by slug.",
        responses={200: NewsSerializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["News"],
        operation_summary="Create news",
        operation_description="Admin-only endpoint for creating a news item.",
        request_body=NewsSerializer,
        responses={201: NewsSerializer},
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["News"],
        operation_summary="Replace news",
        operation_description="Admin-only endpoint for replacing a news item.",
        request_body=NewsSerializer,
        responses={200: NewsSerializer},
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["News"],
        operation_summary="Update news",
        operation_description="Admin-only endpoint for partially updating a news item.",
        request_body=NewsSerializer,
        responses={200: NewsSerializer},
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["News"],
        operation_summary="Delete news",
        operation_description="Admin-only endpoint for deleting a news item.",
        responses={204: "No content"},
    ),
)
class NewsViewSet(NewsWritePermissionMixin, viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = News.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True, published_at__lte=timezone.now())
        return queryset


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="List wishlist",
        operation_description="Returns products saved in the current user's wishlist.",
        responses={200: WishlistItemSerializer(many=True)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="Get wishlist item",
        operation_description="Returns one wishlist item owned by the current user.",
        responses={200: WishlistItemSerializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="Add product to wishlist",
        operation_description="Adds a product to the current user's wishlist.",
        request_body=WishlistItemSerializer,
        responses={201: WishlistItemSerializer},
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="Replace wishlist item",
        operation_description="Replaces the product stored in one wishlist item owned by the current user.",
        request_body=WishlistItemSerializer,
        responses={200: WishlistItemSerializer},
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="Update wishlist item",
        operation_description="Partially updates one wishlist item owned by the current user.",
        request_body=WishlistItemSerializer,
        responses={200: WishlistItemSerializer},
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="Remove wishlist item",
        operation_description="Removes a product from the current user's wishlist.",
        responses={204: "No content"},
    ),
)
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=["Wishlist"],
        operation_summary="Toggle wishlist product",
        operation_description="Adds the product if it is not saved; removes it if it already exists.",
        request_body=WishlistToggleSerializer,
        responses={200: WISHLIST_TOGGLE_RESPONSE, 201: WISHLIST_TOGGLE_RESPONSE},
    )
    @action(detail=False, methods=("post",))
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
        return Response({"in_wishlist": True, "item": serializer.data}, status=status.HTTP_201_CREATED)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["Order Addresses"],
        operation_summary="List order addresses",
        operation_description="Returns saved delivery/order addresses for the current user.",
        responses={200: OrderAddressSerializer(many=True)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["Order Addresses"],
        operation_summary="Get order address",
        operation_description="Returns one saved address owned by the current user.",
        responses={200: OrderAddressSerializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["Order Addresses"],
        operation_summary="Create order address",
        operation_description="Creates a delivery/order address for the current user.",
        request_body=OrderAddressSerializer,
        responses={201: OrderAddressSerializer},
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["Order Addresses"],
        operation_summary="Replace order address",
        operation_description="Replaces a saved address owned by the current user.",
        request_body=OrderAddressSerializer,
        responses={200: OrderAddressSerializer},
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["Order Addresses"],
        operation_summary="Update order address",
        operation_description="Partially updates a saved address owned by the current user.",
        request_body=OrderAddressSerializer,
        responses={200: OrderAddressSerializer},
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["Order Addresses"],
        operation_summary="Delete order address",
        operation_description="Deletes a saved address owned by the current user.",
        responses={204: "No content"},
    ),
)
class OrderAddressViewSet(viewsets.ModelViewSet):
    serializer_class = OrderAddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrderAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["Order Reviews"],
        operation_summary="List order reviews",
        operation_description="Returns reviews created by the current user. Use order to filter by order id.",
        manual_parameters=ORDER_REVIEW_PARAMS,
        responses={200: OrderReviewSerializer(many=True)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["Order Reviews"],
        operation_summary="Get order review",
        operation_description="Returns one order review owned by the current user.",
        responses={200: OrderReviewSerializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["Order Reviews"],
        operation_summary="Create order review",
        operation_description="Creates one review for one of the current user's orders.",
        request_body=OrderReviewSerializer,
        responses={201: OrderReviewSerializer},
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["Order Reviews"],
        operation_summary="Replace order review",
        operation_description="Replaces an order review owned by the current user.",
        request_body=OrderReviewSerializer,
        responses={200: OrderReviewSerializer},
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["Order Reviews"],
        operation_summary="Update order review",
        operation_description="Partially updates an order review owned by the current user.",
        request_body=OrderReviewSerializer,
        responses={200: OrderReviewSerializer},
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["Order Reviews"],
        operation_summary="Delete order review",
        operation_description="Deletes an order review owned by the current user.",
        responses={204: "No content"},
    ),
)
class OrderReviewViewSet(viewsets.ModelViewSet):
    serializer_class = OrderReviewSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = OrderReview.objects.filter(user=self.request.user).select_related("order")
        order_id = self.request.query_params.get("order")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["Product Comparisons"],
        operation_summary="List saved comparisons",
        operation_description="Returns saved product comparison groups for the current user.",
        responses={200: ProductComparisonSerializer(many=True)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["Product Comparisons"],
        operation_summary="Get saved comparison",
        operation_description="Returns one saved comparison group owned by the current user.",
        responses={200: ProductComparisonSerializer},
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["Product Comparisons"],
        operation_summary="Create saved comparison",
        operation_description="Saves a named product comparison group for the current user.",
        request_body=ProductComparisonSerializer,
        responses={201: ProductComparisonSerializer},
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["Product Comparisons"],
        operation_summary="Replace saved comparison",
        operation_description="Replaces a saved product comparison group owned by the current user.",
        request_body=ProductComparisonSerializer,
        responses={200: ProductComparisonSerializer},
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["Product Comparisons"],
        operation_summary="Update saved comparison",
        operation_description="Partially updates a saved product comparison group owned by the current user.",
        request_body=ProductComparisonSerializer,
        responses={200: ProductComparisonSerializer},
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["Product Comparisons"],
        operation_summary="Delete saved comparison",
        operation_description="Deletes a saved product comparison group owned by the current user.",
        responses={204: "No content"},
    ),
)
class ProductComparisonViewSet(viewsets.ModelViewSet):
    serializer_class = ProductComparisonSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ProductComparison.objects.filter(user=self.request.user).prefetch_related("products")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductDiscoveryView(APIView):
    permission_classes = (AllowAny,)

    def _base_queryset(self):
        product_model = get_product_model()
        queryset = product_model.objects.all()
        field_names = _model_field_names(product_model)
        relation_names = _relation_field_names(product_model)

        if "is_active" in field_names:
            queryset = queryset.filter(is_active=True)
        if "is_available" in field_names:
            queryset = queryset.filter(is_available=True)

        if "category" in relation_names:
            queryset = queryset.select_related("category") if "category" in field_names else queryset
        if "brand" in relation_names:
            queryset = queryset.select_related("brand") if "brand" in field_names else queryset
        return queryset

    def _filter_text_relation(self, queryset, relation, value):
        model = queryset.model
        field_names = _model_field_names(model)
        if relation not in _relation_field_names(model):
            if relation in field_names:
                return queryset.filter(**{f"{relation}__iexact": value})
            return queryset

        relation_field = model._meta.get_field(relation)
        related_model = getattr(relation_field, "related_model", None)
        related_fields = _model_field_names(related_model) if related_model else set()
        lookup = Q()
        if str(value).isdigit():
            lookup |= Q(**{f"{relation}__pk": value})
        for key in ("slug", "name", "title"):
            if key in related_fields:
                lookup |= Q(**{f"{relation}__{key}__iexact": value})
        if not lookup.children:
            return queryset
        return queryset.filter(lookup)

    def _apply_filters(self, queryset):
        params = self.request.query_params
        model = queryset.model
        fields = _model_field_names(model)
        relations = _relation_field_names(model)

        search = params.get("search")
        if search:
            lookup = Q()
            for field in ("name", "title", "description", "short_description", "sku"):
                if field in fields:
                    lookup |= Q(**{f"{field}__icontains": search})
            if lookup:
                queryset = queryset.filter(lookup)

        for relation in ("category", "brand", "color", "size"):
            value = params.get(relation)
            if value:
                queryset = self._filter_text_relation(queryset, relation, value)

        price_field = next((field for field in ("price", "new_price", "sale_price") if field in fields), None)
        if price_field:
            min_price = params.get("min_price")
            max_price = params.get("max_price")
            if min_price:
                queryset = queryset.filter(**{f"{price_field}__gte": min_price})
            if max_price:
                queryset = queryset.filter(**{f"{price_field}__lte": max_price})

        if params.get("in_stock") in ("true", "1", "yes"):
            if "quantity" in fields:
                queryset = queryset.filter(quantity__gt=0)
            elif "stock" in fields:
                queryset = queryset.filter(stock__gt=0)
            elif "in_stock" in fields:
                queryset = queryset.filter(in_stock=True)

        if params.get("has_discount") in ("true", "1", "yes"):
            if "discount" in fields:
                queryset = queryset.filter(discount__gt=0)
            elif "old_price" in fields and price_field:
                queryset = queryset.filter(old_price__gt=F(price_field))

        if params.get("is_new") in ("true", "1", "yes"):
            if "is_new" in fields:
                queryset = queryset.filter(is_new=True)
            elif "created_at" in fields:
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))

        if params.get("popular") in ("true", "1", "yes"):
            queryset = self._annotate_popularity(queryset).order_by("-popularity", "-id")

        ordering = params.get("ordering")
        if ordering:
            queryset = self._apply_ordering(queryset, ordering, fields)

        return queryset.distinct()

    def _annotate_popularity(self, queryset):
        if "order_items" in _relation_field_names(queryset.model):
            return queryset.annotate(popularity=Count("order_items", distinct=True))
        if "commerce_wishlist_items" in _relation_field_names(queryset.model):
            return queryset.annotate(popularity=Count("commerce_wishlist_items", distinct=True))
        return queryset.annotate(popularity=Count("id"))

    def _apply_ordering(self, queryset, ordering, fields):
        desc = ordering.startswith("-")
        raw_field = ordering[1:] if desc else ordering
        direction = "-" if desc else ""

        aliases = {
            "price": next((field for field in ("price", "new_price", "sale_price") if field in fields), None),
            "name": next((field for field in ("name", "title") if field in fields), None),
            "created_at": "created_at" if "created_at" in fields else None,
            "rating": "rating" if "rating" in fields else None,
        }

        if raw_field == "popularity":
            return self._annotate_popularity(queryset).order_by(f"{direction}popularity", "-id")

        field = aliases.get(raw_field, raw_field if raw_field in fields else None)
        if field:
            return queryset.order_by(f"{direction}{field}")
        return queryset

    @swagger_auto_schema(
        tags=["Product List"],
        operation_summary="Filter products",
        operation_description=(
            "Product listing endpoint with search, category, brand, color, size, price, stock, "
            "discount, new-product, popularity, ordering, and pagination filters."
        ),
        manual_parameters=PRODUCT_FILTER_PARAMS,
        responses={200: PRODUCT_DISCOVERY_RESPONSE},
    )
    def get(self, request):
        queryset = self._apply_filters(self._base_queryset())
        page_size = _positive_int(request.query_params.get("page_size"), 20, 100)
        page = _positive_int(request.query_params.get("page"), 1)
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        products = [serialize_product(product, request) for product in queryset[start:end]]
        return Response(
            {
                "count": total,
                "page": page,
                "page_size": page_size,
                "results": products,
            }
        )


def _first_existing_field(instance, candidates):
    fields = _model_field_names(instance.__class__)
    for field in candidates:
        if field in fields:
            return field, getattr(instance, field, None)
    return None, None


def _product_display_name(product):
    field, value = _first_existing_field(product, ("name", "title", "slug", "sku"))
    if value:
        return str(value)
    return str(product)


def _product_cost(product):
    fields = _model_field_names(product.__class__)
    cost = {
        "current": None,
        "current_field": None,
        "old": None,
        "old_field": None,
        "discount": None,
    }

    for field in ("sale_price", "new_price", "discount_price", "price", "cost"):
        if field in fields:
            value = getattr(product, field, None)
            if value is not None:
                cost["current"] = value
                cost["current_field"] = field
                break

    for field in ("old_price", "original_price", "regular_price"):
        if field in fields:
            value = getattr(product, field, None)
            if value is not None:
                cost["old"] = value
                cost["old_field"] = field
                break

    if "discount" in fields:
        cost["discount"] = getattr(product, "discount", None)

    return cost


def _product_stock(product):
    fields = _model_field_names(product.__class__)
    stock = {"quantity": None, "quantity_field": None, "in_stock": None}

    for field in ("stock", "quantity", "qty", "count", "amount"):
        if field in fields:
            value = getattr(product, field, None)
            if value is not None:
                stock["quantity"] = value
                stock["quantity_field"] = field
                try:
                    stock["in_stock"] = value > 0
                except TypeError:
                    stock["in_stock"] = bool(value)
                break

    for field in ("in_stock", "is_in_stock", "available", "is_available"):
        if field in fields:
            stock["in_stock"] = bool(getattr(product, field, False))
            break

    return stock


def _product_review(product):
    fields = _model_field_names(product.__class__)
    review = {
        "average_rating": None,
        "average_rating_field": None,
        "reviews_count": None,
        "reviews_count_field": None,
    }

    for field in ("average_rating", "avg_rating", "rating", "stars"):
        if field in fields:
            value = getattr(product, field, None)
            if value is not None:
                review["average_rating"] = value
                review["average_rating_field"] = field
                break

    for field in ("reviews_count", "review_count", "rating_count", "comments_count"):
        if field in fields:
            value = getattr(product, field, None)
            if value is not None:
                review["reviews_count"] = value
                review["reviews_count_field"] = field
                break

    for relation in product._meta.get_fields():
        relation_name = relation.name
        if "review" not in relation_name.lower():
            continue

        manager = getattr(product, relation_name, None)
        if not hasattr(manager, "all"):
            continue

        queryset = manager.all()
        if review["reviews_count"] is None:
            review["reviews_count"] = queryset.count()
            review["reviews_count_field"] = relation_name

        related_fields = _model_field_names(queryset.model)
        if review["average_rating"] is None:
            for field in ("rating", "rate", "stars"):
                if field in related_fields:
                    review["average_rating"] = queryset.aggregate(value=Avg(field))["value"]
                    review["average_rating_field"] = f"{relation_name}.{field}"
                    break
        break

    return review


def _product_compare_row(product):
    return {
        "product_id": product.pk,
        "product_name": _product_display_name(product),
        "cost": _product_cost(product),
        "stock": _product_stock(product),
        "review": _product_review(product),
    }


class ProductCompareView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=["Product Compare"],
        operation_summary="Compare products",
        operation_description="Compares 2 to 6 products and returns product data plus common comparable fields.",
        request_body=ProductCompareRequestSerializer,
        responses={200: PRODUCT_COMPARE_RESPONSE},
    )
    def post(self, request):
        serializer = ProductCompareRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_ids = serializer.validated_data["product_ids"]
        product_model = get_product_model()
        products = list(product_model.objects.filter(pk__in=product_ids))
        products.sort(key=lambda product: product_ids.index(product.pk))

        if len(products) != len(product_ids):
            found_ids = {product.pk for product in products}
            missing_ids = [product_id for product_id in product_ids if product_id not in found_ids]
            return Response({"product_ids": [f"Products not found: {missing_ids}"]}, status=404)

        serialized = [serialize_product(product, request) for product in products]
        comparison = [_product_compare_row(product) for product in products]
        comparable_fields = sorted(set.intersection(*(set(item.keys()) for item in serialized)))
        return Response(
            {
                "products": serialized,
                "comparison": comparison,
                "comparable_fields": comparable_fields,
            }
        )


class HomeView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=["Home"],
        operation_summary="Home page data",
        operation_description="Returns popular products and latest published news for the home page.",
        manual_parameters=HOME_PARAMS,
        responses={200: HOME_RESPONSE},
    )
    def get(self, request):
        product_model = get_product_model()
        queryset = product_model.objects.all()
        fields = _model_field_names(product_model)
        relations = _relation_field_names(product_model)

        if "is_active" in fields:
            queryset = queryset.filter(is_active=True)
        if "is_available" in fields:
            queryset = queryset.filter(is_available=True)
        if "order_items" in relations:
            queryset = queryset.annotate(popularity=Count("order_items", distinct=True)).order_by(
                "-popularity", "-id"
            )
        elif "commerce_wishlist_items" in relations:
            queryset = queryset.annotate(popularity=Count("commerce_wishlist_items", distinct=True)).order_by(
                "-popularity", "-id"
            )
        elif "views_count" in fields:
            queryset = queryset.order_by("-views_count", "-id")
        elif "created_at" in fields:
            queryset = queryset.order_by("-created_at", "-id")
        else:
            queryset = queryset.order_by("-id")

        limit = _positive_int(request.query_params.get("limit"), 12, 50)
        products = [serialize_product(product, request) for product in queryset[:limit]]
        news = NewsSerializer(
            News.objects.filter(is_published=True, published_at__lte=timezone.now())[:6],
            many=True,
            context={"request": request},
        ).data
        return Response({"popular_products": products, "latest_news": news})


class UserOrdersView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Account"],
        operation_summary="Current user orders",
        operation_description="Returns orders that belong to the authenticated user.",
        responses={200: _array_schema(ORDER_OBJECT_SCHEMA)},
    )
    def get(self, request):
        order_model = get_order_model()
        fields = _model_field_names(order_model)
        queryset = order_model.objects.all()

        if "user" in fields:
            queryset = queryset.filter(user=request.user)
        elif "customer" in fields:
            queryset = queryset.filter(customer=request.user)
        else:
            return Response(
                {"detail": "Order model has no user/customer field to filter current user orders."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if "created_at" in fields:
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("-id")

        return Response([serialize_order(order, request) for order in queryset])


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Account"],
        operation_summary="Current user profile",
        operation_description="Returns the authenticated user's profile.",
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        return Response(UserProfileSerializer(request.user, context={"request": request}).data)

    @swagger_auto_schema(
        tags=["Account"],
        operation_summary="Update current user profile",
        operation_description="Partially updates editable fields on the authenticated user's profile.",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer},
    )
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Account"],
        operation_summary="Update current user password",
        operation_description="Changes the authenticated user's password after checking the old password.",
        request_body=ChangePasswordSerializer,
        responses={200: PASSWORD_RESPONSE},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."})


class ChangeUsernameView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Account"],
        operation_summary="Update current user username",
        operation_description="Changes the authenticated user's username.",
        request_body=ChangeUsernameSerializer,
        responses={200: USERNAME_RESPONSE},
    )
    def post(self, request):
        serializer = ChangeUsernameSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "Username updated successfully.", "username": user.username})

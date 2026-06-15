from importlib import import_module

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Discount, News, OrderAddress, OrderReview, ProductComparison, WishlistItem


def get_product_model():
    return apps.get_model("product", "Product")


def get_order_model():
    return apps.get_model("order", "Order")


def _model_field_names(model):
    return {field.name for field in model._meta.fields}


def _serializer_from_app(module_path, class_names):
    try:
        module = import_module(module_path)
    except Exception:
        return None

    for class_name in class_names:
        serializer_class = getattr(module, class_name, None)
        if serializer_class is not None:
            return serializer_class
    return None


def serialize_product(product, request=None):
    serializer_class = _serializer_from_app(
        "apps.product.serializers",
        ("ProductSerializer", "ProductListSerializer", "ProductDetailSerializer"),
    )
    if serializer_class is not None:
        try:
            return serializer_class(product, context={"request": request}).data
        except Exception:
            pass

    return serialize_model_fallback(product, request)


def serialize_order(order, request=None):
    serializer_class = _serializer_from_app(
        "apps.order.serializers",
        ("OrderSerializer", "OrderListSerializer", "OrderDetailSerializer"),
    )
    if serializer_class is not None:
        try:
            return serializer_class(order, context={"request": request}).data
        except Exception:
            pass

    return serialize_model_fallback(order, request)


def serialize_model_fallback(instance, request=None):
    data = {"id": instance.pk}
    for field in instance._meta.fields:
        if field.is_relation:
            value = getattr(instance, f"{field.name}_id", None)
        else:
            value = getattr(instance, field.name, None)
            try:
                url = value.url
            except (AttributeError, ValueError):
                pass
            else:
                value = request.build_absolute_uri(url) if request else url
        data[field.name] = value
    return data


class DynamicProductField(serializers.Field):
    def to_representation(self, value):
        return serialize_product(value, self.context.get("request"))


class DynamicOrderField(serializers.Field):
    def to_representation(self, value):
        return serialize_order(value, self.context.get("request"))


class WishlistItemSerializer(serializers.ModelSerializer):
    product_detail = DynamicProductField(source="product", read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "product", "product_detail", "created_at")
        read_only_fields = ("id", "product_detail", "created_at")

    def validate_product(self, product):
        request = self.context["request"]
        if self.instance is None and WishlistItem.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError("Product is already in wishlist.")
        return product


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = (
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "image",
            "is_published",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class DiscountSerializer(serializers.ModelSerializer):
    products_detail = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = (
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "image",
            "discount_percent",
            "products",
            "products_detail",
            "is_published",
            "starts_at",
            "ends_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "products_detail", "created_at", "updated_at")

    def get_products_detail(self, obj):
        request = self.context.get("request")
        return [serialize_product(product, request) for product in obj.products.all()]


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone",
            "country",
            "region",
            "city",
            "district",
            "street",
            "house",
            "apartment",
            "postal_code",
            "note",
            "is_default",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class OrderReviewSerializer(serializers.ModelSerializer):
    order_detail = DynamicOrderField(source="order", read_only=True)

    class Meta:
        model = OrderReview
        fields = ("id", "order", "order_detail", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "order_detail", "created_at", "updated_at")

    def validate_order(self, order):
        request = self.context["request"]
        user_fields = {field.name for field in order._meta.fields}
        if "user" in user_fields and order.user_id != request.user.id:
            raise serializers.ValidationError("You can review only your own orders.")
        if "customer" in user_fields and getattr(order, "customer_id", None) != request.user.id:
            raise serializers.ValidationError("You can review only your own orders.")
        return order

    def validate(self, attrs):
        request = self.context["request"]
        order = attrs.get("order") or getattr(self.instance, "order", None)
        if self.instance is None and order is not None:
            exists = OrderReview.objects.filter(user=request.user, order=order).exists()
            if exists:
                raise serializers.ValidationError("You already reviewed this order.")
        return attrs


class ProductComparisonSerializer(serializers.ModelSerializer):
    products_detail = serializers.SerializerMethodField()

    class Meta:
        model = ProductComparison
        fields = ("id", "name", "products", "products_detail", "created_at", "updated_at")
        read_only_fields = ("id", "products_detail", "created_at", "updated_at")

    def validate_products(self, products):
        if len(products) < 2:
            raise serializers.ValidationError("Choose at least 2 products to compare.")
        if len(products) > 6:
            raise serializers.ValidationError("You can compare up to 6 products.")
        return products

    def get_products_detail(self, obj):
        request = self.context.get("request")
        return [serialize_product(product, request) for product in obj.products.all()]


class ProductCompareRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=2,
        max_length=6,
    )

    def validate_product_ids(self, product_ids):
        unique_ids = list(dict.fromkeys(product_ids))
        if len(unique_ids) < 2:
            raise serializers.ValidationError("Choose at least 2 different products.")
        return unique_ids


class WishlistToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)


class UserProfileSerializer(serializers.ModelSerializer):
    @staticmethod
    def get_profile_fields():
        user_model = get_user_model()
        model_fields = _model_field_names(user_model)
        return tuple(
            field
            for field in (
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "phone",
                "avatar",
                "image",
            )
            if field in model_fields
        )

    class Meta:
        model = get_user_model()
        fields = "__all__"

    def get_field_names(self, declared_fields, info):
        return self.get_profile_fields()

    def get_fields(self):
        fields = super().get_fields()
        for field_name in ("id", "username"):
            if field_name in fields:
                fields[field_name].read_only = True
        return fields


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, old_password):
        user = self.context["request"].user
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect.")
        return old_password

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class ChangeUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    def validate_username(self, username):
        user_model = get_user_model()
        user = self.context["request"].user
        username_field = getattr(user_model, "USERNAME_FIELD", "username")

        if username_field != "username" or "username" not in _model_field_names(user_model):
            raise serializers.ValidationError("This project does not use username as the login field.")

        if user_model.objects.exclude(pk=user.pk).filter(username__iexact=username).exists():
            raise serializers.ValidationError("This username is already taken.")
        return username

    def save(self, **kwargs):
        user = self.context["request"].user
        user.username = self.validated_data["username"]
        user.save(update_fields=["username"])
        return user
from rest_framework import serializers

try:
    from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
except ImportError:
    OpenApiExample = None
    extend_schema_serializer = None


def swagger_serializer(*args, **kwargs):
    if extend_schema_serializer is None:
        return lambda serializer_class: serializer_class
    return extend_schema_serializer(*args, **kwargs)


@swagger_serializer(
    examples=[
        OpenApiExample(
            "Home category",
            value={
                "title": "Сантехника",
                "image": "/media/home/categories/plumbing.png",
                "url": "/catalog/santehnika/",
            },
        ),
        OpenApiExample(
            "Catalog shortcut",
            value={
                "title": "Перейти в каталог",
                "image": None,
                "url": "/catalog/",
            },
        ),
    ]
    if OpenApiExample is not None
    else None,
)
class HomeCategorySerializer(serializers.Serializer):
    title = serializers.CharField()
    image = serializers.ImageField(required=False, allow_null=True)
    url = serializers.CharField(required=False)


@swagger_serializer(
    examples=[
        OpenApiExample(
            "Home catalog shortcut",
            value={
                "title": "Перейти в каталог",
                "url": "/catalog/",
            },
        )
    ]
    if OpenApiExample is not None
    else None,
)
class HomeCatalogShortcutSerializer(serializers.Serializer):
    title = serializers.CharField(default="Перейти в каталог")
    url = serializers.CharField(default="/catalog/")


class HomeCategoriesSwaggerSerializer(serializers.Serializer):
    categories = HomeCategorySerializer(many=True)
    catalog = HomeCatalogShortcutSerializer()

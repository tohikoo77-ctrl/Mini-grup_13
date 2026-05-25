from django.contrib import admin

from .models import News, OrderAddress, OrderReview, ProductComparison, WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    raw_id_fields = ("user", "product")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published", "published_at", "created_at")
    list_filter = ("is_published", "published_at", "created_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "phone", "is_default", "created_at")
    list_filter = ("is_default", "city", "created_at")
    search_fields = ("first_name", "last_name", "phone", "city", "street")


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment",)


@admin.register(ProductComparison)
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "created_at", "updated_at")
    search_fields = ("name",)
    filter_horizontal = ("products",)

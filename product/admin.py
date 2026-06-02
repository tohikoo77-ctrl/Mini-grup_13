from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'price',
        'old_price',
        'discount_percent',
        'stock',
        'is_hit',
        'is_new',
        'is_sale',
        'created_at',
        'updated_at',
    )
    list_filter = ('category', 'is_hit', 'is_new', 'is_sale')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

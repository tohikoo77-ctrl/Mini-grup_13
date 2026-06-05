from django.contrib import admin
from .models import ShippingMethod, OrderTracking


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'delivery_days', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order', 'status', 'shipped_date', 'delivered_date']
    list_filter = ['status', 'created_at']
    search_fields = ['tracking_number', 'order__id']
    readonly_fields = ['created_at', 'updated_at']

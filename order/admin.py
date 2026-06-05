from django.contrib import admin
from .models import Order, OrderItem, ReturnRequest


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price',)


class ReturnRequestInline(admin.TabularInline):
    model = ReturnRequest
    extra = 0
    readonly_fields = ('requested_at', 'approved_at', 'received_at', 'completed_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    inlines = [OrderItemInline, ReturnRequestInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'get_total_price')
    list_filter = ('order__status',)
    search_fields = ('order__user__username', 'product__name')


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'order_item', 'reason', 'status', 'requested_at')
    list_filter = ('status', 'reason', 'requested_at')
    search_fields = ('order__user__username', 'order_item__product__name', 'description')
    readonly_fields = ('requested_at', 'approved_at', 'received_at', 'completed_at', 'updated_at')
    fieldsets = (
        ('Return Info', {
            'fields': ('order', 'order_item', 'reason', 'description')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'admin_notes', 'requested_at', 'approved_at', 'received_at', 'completed_at')
        }),
        ('Refund', {
            'fields': ('return_shipping_cost', 'refund_amount')
        }),
    )

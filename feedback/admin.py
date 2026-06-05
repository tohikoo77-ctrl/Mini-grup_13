from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'rating', 'user', 'is_read', 'is_resolved', 'created_at']
    list_filter = ['category', 'rating', 'is_read', 'is_resolved', 'created_at']
    search_fields = ['title', 'message', 'user__email', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Feedback Info', {
            'fields': ('category', 'rating', 'title', 'message')
        }),
        ('User Info', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Status', {
            'fields': ('is_read', 'is_resolved', 'admin_response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

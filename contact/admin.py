from django.contrib import admin
from .models import ContactMessage, MessageReply


class MessageReplyInline(admin.TabularInline):
    model = MessageReply
    extra = 1
    fields = ['sender', 'content', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'priority', 'sender_email', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'assigned_to']
    search_fields = ['subject', 'message', 'sender_email', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageReplyInline]
    fieldsets = (
        ('Message Info', {
            'fields': ('subject', 'message', 'status', 'priority')
        }),
        ('Sender Info', {
            'fields': ('user', 'sender_name', 'sender_email', 'sender_phone')
        }),
        ('Management', {
            'fields': ('assigned_to', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MessageReply)
class MessageReplyAdmin(admin.ModelAdmin):
    list_display = ['message', 'sender', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['content', 'message__subject']
    readonly_fields = ['created_at', 'updated_at']

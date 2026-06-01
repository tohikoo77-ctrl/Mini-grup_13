from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailVerificationCode, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("is_active", "is_staff", "role")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Information", {"fields": ("phone_number", "role", "address")}),
        (
            "Verification",
            {"fields": ("verification_code", "verification_code_expires_at")},
        ),
    )


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("email", "code", "is_used", "created_at", "user")
    list_filter = ("is_used",)
    search_fields = ("email", "code")
    ordering = ("-created_at",)
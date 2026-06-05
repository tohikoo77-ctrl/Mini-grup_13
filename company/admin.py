from django.contrib import admin
from .models import CompanyInfo, TeamMember


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'country']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'mission', 'vision', 'established_year', 'logo', 'cover_image')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'address', 'city', 'country')
        }),
        ('Social Links', {
            'fields': ('website', 'facebook', 'instagram', 'twitter', 'linkedin')
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'company', 'email', 'is_active', 'order']
    list_filter = ['position', 'is_active', 'company']
    search_fields = ['name', 'email']
    ordering = ['order', 'name']

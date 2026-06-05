from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class CompanyInfo(models.Model):
    """Company information and details"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    established_year = models.IntegerField(blank=True, null=True)
    
    # Contact Info
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # Social Links
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    # Additional
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='company/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Company team members"""
    POSITION_CHOICES = [
        ('ceo', 'CEO'),
        ('cto', 'CTO'),
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('marketing', 'Marketing'),
        ('support', 'Customer Support'),
        ('other', 'Other'),
    ]

    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Social
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    profile_image = models.ImageField(upload_to='team/', blank=True, null=True)
    
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.position}"

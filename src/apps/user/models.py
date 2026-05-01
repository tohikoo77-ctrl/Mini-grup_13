from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
# Create your models here.


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        CUSTOMER = 'customer', 'Customer'
        SELLER = 'seller', 'Seller'
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=13, 
        blank=True, 
        null=True,
        validators=[RegexValidator(
            regex=r'^\+998\d{9}$',
            message="Phone number must be entered in the format: '+998XXXXXXXXX'."
        )])
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.username
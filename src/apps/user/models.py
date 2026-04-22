from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        CUSTOMER = 'customer', 'Customer'
        SELLER = 'seller', 'Seller'
    email = models.CharField(unique=True)
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
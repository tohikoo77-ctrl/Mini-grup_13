from django.db import models
from category.models import Category
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    price = models.CharField(max_length=255)
    old_price = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    specifications = models.JSONField(default=dict, blank=True)
    advantages = models.JSONField(default=list, blank=True)
    is_hit = models.BooleanField(default=False)
    is_new = models.BooleanField()
    is_sale = models.BooleanField()
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
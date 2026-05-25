from django.db import models
from user.models import User
from product.models import Product
# Create your models here.

class Cart(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):        
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"
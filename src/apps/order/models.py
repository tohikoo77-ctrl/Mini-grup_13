from django.db import models
from apps.user.models import User
from apps.product.models import Product
# Create your models here.

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        AWAITING_PAYMENT = 'AWAITING_PAYMENT', 'Awaiting Payment'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def calculate_total_price(self):
        """Calculate total price from order items"""
        return sum(item.quantity * item.price for item in self.items.all())

    def update_total_price(self):
        """Update the total price based on current items"""
        self.total_price = self.calculate_total_price()
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField()  # Price at the time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def get_total_price(self):
        """Calculate total price for this item"""
        return self.quantity * self.price
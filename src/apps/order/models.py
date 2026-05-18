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

from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender="order.OrderItem")
def set_order_item_price(sender, instance, **kwargs):
    if not instance.product_id:
        return

    unit_price = instance.product.price
    quantity = instance.quantity or 1
    subtotal = unit_price * quantity

    discount_sum = (
        getattr(instance, "discount_sum", 0)
        or getattr(instance, "discount_amount", 0)
        or 0
    )
    discount_percent = getattr(instance, "discount_percent", 0) or 0
    discount = discount_sum + (subtotal * discount_percent / 100)
    total_price = max(subtotal - discount, 0)

    if instance.price is None:
        instance.price = unit_price

    if hasattr(instance, "total_price"):
        instance.total_price = total_price
    elif hasattr(instance, "total"):
        instance.total = total_price

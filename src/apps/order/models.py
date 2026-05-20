from django.db import models
from apps.user.models import User
from apps.product.models import Product
from decimal import Decimal


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
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def calculate_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def update_total_price(self):
        self.total_price = self.calculate_total_price()
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.price * self.quantity


from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=OrderItem)
def set_order_item_price(sender, instance, **kwargs):
    if not instance.product_id:
        return

    unit_price = Decimal(instance.product.price)
    quantity = int(instance.quantity or 1)

    subtotal = unit_price * quantity

    discount_sum = Decimal(getattr(instance, "discount_sum", 0) or 0)
    discount_percent = Decimal(getattr(instance, "discount_percent", 0) or 0)

    discount = discount_sum + (subtotal * discount_percent / Decimal("100"))

    total_price = max(subtotal - discount, Decimal("0"))

    instance.price = unit_price
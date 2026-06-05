from django.db import models
from user.models import User
from product.models import Product
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


class ReturnRequest(models.Model):
    """Return request for orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    REASON_CHOICES = [
        ('defective', 'Defective Product'),
        ('damaged', 'Damaged in Shipping'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_requests')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(help_text="Detailed explanation of the return")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Notes from admin")
    
    return_shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Cost for return shipping, if customer needs to pay"
    )
    refund_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Amount to be refunded"
    )
    
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_at']
        verbose_name_plural = "Return Requests"

    def __str__(self):
        return f"Return for Order {self.order_id} - {self.status}"
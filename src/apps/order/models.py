from django.db import models
from apps.user.models import User
# Create your models here.

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        AWAITING_PAYMENT = 'AWAITING_PAYMENT', 'Awaiting Payment'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIIPPED = 'SHIPPED', 'Shipped'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
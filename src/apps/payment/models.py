from django.db import models
from apps.order.models import Order
# Create your models here.

class Payment(models.Model):
    class Method(models.TextChoices):
        CARD = 'CARD', 'Card'
        CASH = 'CASH', 'Cash'
        CLICK = 'CLICK', 'Click'
        PAYME = 'PAYME', 'Payme'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'
        CANCELED = 'CANCELED', 'Canceled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField()
    method = models.CharField(max_length=10, choices=Method.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment {self.id} for Order {self.order.id} - {self.status}'
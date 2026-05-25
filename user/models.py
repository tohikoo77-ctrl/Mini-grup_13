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
from random import randint

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class EmailVerificationCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_codes",
    )
    email = models.EmailField()
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.email}: {self.code}"


def send_user_verification_code(user):
    email = getattr(user, "email", None)
    if not email:
        return None

    code = str(randint(100000, 999999))
    verification = EmailVerificationCode.objects.create(
        user=user,
        email=email,
        code=code,
    )

    send_mail(
        subject="Verification code",
        message=f"Your verification code is {code}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[email],
        fail_silently=False,
    )
    return verification


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_verification_code_after_user_create(sender, instance, created, **kwargs):
    if created:
        send_user_verification_code(instance)


@receiver(user_logged_in)
def send_verification_code_after_user_login(sender, request, user, **kwargs):
    send_user_verification_code(user)

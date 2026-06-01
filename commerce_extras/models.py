from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class NewsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())

    def daily(self):
        cutoff = timezone.now() - timedelta(hours=24)
        return self.published().filter(published_at__gte=cutoff)


class NewsManager(models.Manager.from_queryset(NewsQuerySet)):
    pass


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE,
        related_name="commerce_wishlist_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "product"),
                name="unique_user_wishlist_product",
            )
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.product_id}"


class News(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    image = models.FileField(upload_to="news/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NewsManager()

    class Meta:
        ordering = ("-published_at", "-created_at")
        verbose_name_plural = "news"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:240] or "news"
            slug = base_slug
            index = 2
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{index}"
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class OrderAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_addresses",
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40)
    country = models.CharField(max_length=120, default="Uzbekistan")
    region = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=80, blank=True)
    apartment = models.CharField(max_length=80, blank=True)
    postal_code = models.CharField(max_length=30, blank=True)
    note = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_default", "-created_at")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            OrderAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )

    def __str__(self):
        return f"{self.city}, {self.street}"


class OrderReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_reviews",
    )
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="commerce_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "order"),
                name="unique_user_order_review",
            )
        ]

    def __str__(self):
        return f"Order {self.order_id}: {self.rating}/5"


class ProductComparison(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_comparisons",
    )
    name = models.CharField(max_length=120, blank=True)
    products = models.ManyToManyField("product.Product", related_name="commerce_comparisons")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-created_at")

    def __str__(self):
        return self.name or f"Comparison #{self.pk}"

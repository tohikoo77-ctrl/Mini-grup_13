from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Feedback(models.Model):
    """User feedback and suggestions for the company"""
    CATEGORY_CHOICES = [
        ('suggestion', 'Suggestion'),
        ('complaint', 'Complaint'),
        ('appreciation', 'Appreciation'),
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('other', 'Other'),
    ]

    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='suggestion')
    rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Contact info (if not logged in)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)
    
    attachments = models.JSONField(default=list, blank=True, help_text="URLs of attached files")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"{self.title} - {self.category}"

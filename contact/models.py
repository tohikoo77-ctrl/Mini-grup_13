from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ContactMessage(models.Model):
    """Contact messages from users"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_messages', null=True, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    # Sender info (if not logged in)
    sender_name = models.CharField(max_length=150, blank=True)
    sender_email = models.EmailField(blank=True)
    sender_phone = models.CharField(max_length=20, blank=True)
    
    # Message tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_messages', limit_choices_to={'is_staff': True}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.subject} - {self.status}"


class MessageReply(models.Model):
    """Replies to contact messages"""
    message = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='replies')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='message_replies')
    
    content = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal note not visible to user")
    
    attachments = models.JSONField(default=list, blank=True, help_text="URLs of attached files")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Message Replies"

    def __str__(self):
        return f"Reply to {self.message.subject}"

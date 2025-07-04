from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User


class Notification(models.Model):
    """
    User notifications for various platform events.
    """
    class NotificationType(models.TextChoices):
        JOB_APPLICATION = 'job_application', _('Job Application')
        JOB_ACCEPTED = 'job_accepted', _('Job Accepted')
        JOB_REJECTED = 'job_rejected', _('Job Rejected')
        JOB_COMPLETED = 'job_completed', _('Job Completed')
        PAYMENT_RECEIVED = 'payment_received', _('Payment Received')
        PAYMENT_SENT = 'payment_sent', _('Payment Sent')
        REVIEW_RECEIVED = 'review_received', _('Review Received')
        MESSAGE_RECEIVED = 'message_received', _('Message Received')
        SYSTEM_UPDATE = 'system_update', _('System Update')
        SECURITY_ALERT = 'security_alert', _('Security Alert')
        PROMOTIONAL = 'promotional', _('Promotional')
    
    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')
    
    # Notification Details
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text=_('User receiving the notification')
    )
    
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        help_text=_('Type of notification')
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Notification title')
    )
    
    message = models.TextField(
        help_text=_('Notification message')
    )
    
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text=_('Notification priority')
    )
    
    # Status
    is_read = models.BooleanField(
        default=False,
        help_text=_('Whether the notification has been read')
    )
    
    is_sent = models.BooleanField(
        default=False,
        help_text=_('Whether the notification has been sent')
    )
    
    # Related Data
    related_job_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Related job ID')
    )
    
    related_user_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Related user ID')
    )
    
    related_payment_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Related payment ID')
    )
    
    # Additional Data
    data = models.JSONField(
        default=dict,
        help_text=_('Additional notification data')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When notification was read')
    )
    
    # Delivery
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When notification was sent')
    )
    
    delivery_methods = models.JSONField(
        default=list,
        help_text=_('Methods used to deliver notification (email, push, sms)')
    )
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        from django.utils import timezone
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])
    
    @property
    def is_urgent(self):
        """Check if notification is urgent."""
        return self.priority == self.Priority.URGENT
    
    @property
    def is_high_priority(self):
        """Check if notification is high priority or urgent."""
        return self.priority in [self.Priority.HIGH, self.Priority.URGENT]
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, **kwargs):
        """Create a new notification."""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )
    
    @classmethod
    def create_job_application_notification(cls, client, worker, job):
        """Create notification for new job application."""
        return cls.create_notification(
            user=client,
            notification_type=cls.NotificationType.JOB_APPLICATION,
            title=f"New Application for {job.title}",
            message=f"{worker.get_full_name_or_username()} has applied for your job '{job.title}'",
            related_job_id=job.id,
            related_user_id=worker.id,
            priority=cls.Priority.MEDIUM
        )
    
    @classmethod
    def create_payment_notification(cls, user, payment, is_received=True):
        """Create notification for payment."""
        notification_type = cls.NotificationType.PAYMENT_RECEIVED if is_received else cls.NotificationType.PAYMENT_SENT
        title = f"Payment {'Received' if is_received else 'Sent'}"
        message = f"You have {'received' if is_received else 'sent'} a payment of {payment.amount} {payment.currency}"
        
        return cls.create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_payment_id=payment.payment_id,
            priority=cls.Priority.HIGH
        ) 
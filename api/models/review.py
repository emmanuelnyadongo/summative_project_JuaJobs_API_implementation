from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from .user import User
from .job import Job


class Review(models.Model):
    """
    Reviews and ratings between users for completed jobs.
    """
    class ReviewType(models.TextChoices):
        CLIENT_TO_WORKER = 'client_to_worker', _('Client to Worker')
        WORKER_TO_CLIENT = 'worker_to_client', _('Worker to Client')
    
    # Review Details
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        help_text=_('User giving the review')
    )
    
    reviewed_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        help_text=_('User being reviewed')
    )
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text=_('Job being reviewed')
    )
    
    review_type = models.CharField(
        max_length=20,
        choices=ReviewType.choices,
        help_text=_('Type of review')
    )
    
    # Rating
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating from 1 to 5')
    )
    
    # Review Content
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Review title')
    )
    
    comment = models.TextField(
        help_text=_('Detailed review comment')
    )
    
    # Specific Ratings
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        help_text=_('Communication rating')
    )
    
    quality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        help_text=_('Quality of work rating')
    )
    
    timeliness_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        help_text=_('Timeliness rating')
    )
    
    professionalism_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True,
        help_text=_('Professionalism rating')
    )
    
    # Review Status
    is_public = models.BooleanField(
        default=True,
        help_text=_('Whether the review is public')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the review is verified')
    )
    
    # Response
    response = models.TextField(
        blank=True,
        help_text=_('Response to the review')
    )
    
    response_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Date of response')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ['reviewer', 'reviewed_user', 'job']
        indexes = [
            models.Index(fields=['reviewer']),
            models.Index(fields=['reviewed_user']),
            models.Index(fields=['job']),
            models.Index(fields=['rating']),
            models.Index(fields=['review_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewed_user.username} ({self.rating}/5)"
    
    def save(self, *args, **kwargs):
        """Update user ratings when review is saved."""
        super().save(*args, **kwargs)
        self.reviewed_user.update_rating()
    
    @property
    def is_client_review(self):
        """Check if this is a client reviewing a worker."""
        return self.review_type == self.ReviewType.CLIENT_TO_WORKER
    
    @property
    def is_worker_review(self):
        """Check if this is a worker reviewing a client."""
        return self.review_type == self.ReviewType.WORKER_TO_CLIENT
    
    @property
    def has_response(self):
        """Check if the review has a response."""
        return bool(self.response)
    
    def get_average_specific_rating(self):
        """Calculate average of specific ratings."""
        ratings = [
            self.communication_rating,
            self.quality_rating,
            self.timeliness_rating,
            self.professionalism_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        return sum(valid_ratings) / len(valid_ratings) if valid_ratings else None
    
    def add_response(self, response_text):
        """Add a response to the review."""
        from django.utils import timezone
        self.response = response_text
        self.response_date = timezone.now()
        self.save(update_fields=['response', 'response_date']) 
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for JuaJobs platform.
    Supports both clients (job posters) and workers (job seekers).
    """
    
    class UserType(models.TextChoices):
        CLIENT = 'client', _('Client')
        WORKER = 'worker', _('Worker')
        ADMIN = 'admin', _('Admin')
    
    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')
    
    # Basic Information
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.WORKER,
        help_text=_('Type of user: client, worker, or admin')
    )
    
    # Profile Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text=_('Phone number for contact and verification')
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text=_('User profile picture')
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text=_('User date of birth')
    )
    
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
        null=True,
        help_text=_('User gender')
    )
    
    # Location Information
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('User country')
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('User city')
    )
    
    address = models.TextField(
        blank=True,
        help_text=_('User address')
    )
    
    # Verification and Status
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the user has been verified')
    )
    
    is_active_worker = models.BooleanField(
        default=True,
        help_text=_('Whether the worker is currently active')
    )
    
    # Worker-specific fields
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Worker hourly rate in local currency')
    )
    
    bio = models.TextField(
        blank=True,
        help_text=_('Worker bio/description')
    )
    
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Years of work experience')
    )
    
    # Client-specific fields
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Company name for client users')
    )
    
    company_description = models.TextField(
        blank=True,
        help_text=_('Company description for client users')
    )
    
    # Financial Information
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_('Total earnings for workers')
    )
    
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_('Total amount spent by clients')
    )
    
    # Rating and Reviews
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text=_('Average rating from reviews')
    )
    
    total_reviews = models.PositiveIntegerField(
        default=0,
        help_text=_('Total number of reviews received')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Preferences
    notification_preferences = models.JSONField(
        default=dict,
        help_text=_('User notification preferences')
    )
    
    language_preference = models.CharField(
        max_length=10,
        default='en',
        help_text=_('User language preference')
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_active_worker']),
            models.Index(fields=['country', 'city']),
            models.Index(fields=['average_rating']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_worker(self):
        """Check if user is a worker."""
        return self.user_type == self.UserType.WORKER
    
    @property
    def is_client(self):
        """Check if user is a client."""
        return self.user_type == self.UserType.CLIENT
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.user_type == self.UserType.ADMIN
    
    def update_rating(self):
        """Update average rating based on reviews."""
        from .review import Review
        
        reviews = Review.objects.filter(reviewed_user=self)
        if reviews.exists():
            avg_rating = reviews.aggregate(
                avg=models.Avg('rating')
            )['avg']
            self.average_rating = round(avg_rating, 2)
            self.total_reviews = reviews.count()
            self.save(update_fields=['average_rating', 'total_reviews'])
    
    def get_full_name_or_username(self):
        """Return full name if available, otherwise username."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username 
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from .user import User


class JobCategory(models.Model):
    """
    Categories for jobs to help with organization and search.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Category name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Category description')
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class or identifier')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the category is active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Job Category')
        verbose_name_plural = _('Job Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Job model representing gig work opportunities.
    """
    class JobStatus(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        EXPIRED = 'expired', _('Expired')
    
    class JobType(models.TextChoices):
        HOURLY = 'hourly', _('Hourly')
        FIXED = 'fixed', _('Fixed Price')
        RECURRING = 'recurring', _('Recurring')
    
    class ExperienceLevel(models.TextChoices):
        ENTRY = 'entry', _('Entry Level')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        EXPERT = 'expert', _('Expert')
    
    # Basic Information
    title = models.CharField(
        max_length=200,
        help_text=_('Job title')
    )
    
    description = models.TextField(
        help_text=_('Detailed job description')
    )
    
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text=_('Job category')
    )
    
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        help_text=_('Client who posted the job')
    )
    
    # Job Details
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FIXED,
        help_text=_('Type of job payment')
    )
    
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.ENTRY,
        help_text=_('Required experience level')
    )
    
    # Compensation
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Minimum budget for the job')
    )
    
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Maximum budget for the job')
    )
    
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Hourly rate for hourly jobs')
    )
    
    estimated_hours = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Estimated hours for hourly jobs')
    )
    
    # Requirements and Skills
    required_skills = models.JSONField(
        default=list,
        help_text=_('List of required skills')
    )
    
    preferred_skills = models.JSONField(
        default=list,
        help_text=_('List of preferred skills')
    )
    
    # Location and Timing
    is_remote = models.BooleanField(
        default=False,
        help_text=_('Whether the job can be done remotely')
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Job location')
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('Location latitude')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('Location longitude')
    )
    
    # Timing
    deadline = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Job deadline')
    )
    
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Expected start date')
    )
    
    # Status and Progress
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.OPEN,
        help_text=_('Current job status')
    )
    
    assigned_worker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_jobs',
        help_text=_('Worker assigned to the job')
    )
    
    # Metrics
    views_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of job views')
    )
    
    applications_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of applications received')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(auto_now_add=True)
    
    # Additional Information
    attachments = models.JSONField(
        default=list,
        help_text=_('List of file attachments')
    )
    
    tags = models.JSONField(
        default=list,
        help_text=_('Job tags for search')
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text=_('Whether the job is featured')
    )
    
    is_urgent = models.BooleanField(
        default=False,
        help_text=_('Whether the job is urgent')
    )
    
    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['job_type']),
            models.Index(fields=['category']),
            models.Index(fields=['is_remote']),
            models.Index(fields=['budget_min', 'budget_max']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_urgent']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.client.username}"
    
    def increment_views(self):
        """Increment the view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_applications(self):
        """Increment the applications count."""
        self.applications_count += 1
        self.save(update_fields=['applications_count'])
    
    @property
    def is_open(self):
        """Check if job is open for applications."""
        return self.status == self.JobStatus.OPEN
    
    @property
    def budget_range(self):
        """Get budget range as string."""
        if self.budget_min == self.budget_max:
            return f"${self.budget_min}"
        return f"${self.budget_min} - ${self.budget_max}"


class JobApplication(models.Model):
    """
    Job applications submitted by workers.
    """
    class ApplicationStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        REVIEWING = 'reviewing', _('Reviewing')
        ACCEPTED = 'accepted', _('Accepted')
        REJECTED = 'rejected', _('Rejected')
        WITHDRAWN = 'withdrawn', _('Withdrawn')
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text=_('Job being applied for')
    )
    
    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_applications',
        help_text=_('Worker applying for the job')
    )
    
    # Application Details
    cover_letter = models.TextField(
        help_text=_('Cover letter explaining why the worker is suitable')
    )
    
    proposed_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Worker proposed rate for the job')
    )
    
    estimated_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Estimated duration in hours')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        help_text=_('Application status')
    )
    
    # Client Response
    client_message = models.TextField(
        blank=True,
        help_text=_('Message from client to worker')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Information
    attachments = models.JSONField(
        default=list,
        help_text=_('List of file attachments')
    )
    
    class Meta:
        verbose_name = _('Job Application')
        verbose_name_plural = _('Job Applications')
        ordering = ['-created_at']
        unique_together = ['job', 'worker']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['job', 'worker']),
        ]
    
    def __str__(self):
        return f"{self.worker.username} - {self.job.title}"
    
    def save(self, *args, **kwargs):
        """Override save to update job applications count."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.job.increment_applications()
    
    @property
    def is_pending(self):
        """Check if application is pending."""
        return self.status == self.ApplicationStatus.PENDING
    
    @property
    def is_accepted(self):
        """Check if application is accepted."""
        return self.status == self.ApplicationStatus.ACCEPTED 
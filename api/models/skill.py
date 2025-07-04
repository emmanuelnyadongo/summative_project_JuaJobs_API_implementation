from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from .user import User


class Skill(models.Model):
    """
    Skills that users can have and jobs can require.
    """
    class SkillCategory(models.TextChoices):
        TECHNOLOGY = 'technology', _('Technology')
        DESIGN = 'design', _('Design')
        MARKETING = 'marketing', _('Marketing')
        WRITING = 'writing', _('Writing')
        TRANSLATION = 'translation', _('Translation')
        ADMINISTRATION = 'administration', _('Administration')
        CUSTOMER_SERVICE = 'customer_service', _('Customer Service')
        SALES = 'sales', _('Sales')
        EDUCATION = 'education', _('Education')
        HEALTHCARE = 'healthcare', _('Healthcare')
        LEGAL = 'legal', _('Legal')
        FINANCE = 'finance', _('Finance')
        CONSTRUCTION = 'construction', _('Construction')
        TRANSPORTATION = 'transportation', _('Transportation')
        HOSPITALITY = 'hospitality', _('Hospitality')
        OTHER = 'other', _('Other')
    
    # Skill Details
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Skill name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Skill description')
    )
    
    category = models.CharField(
        max_length=30,
        choices=SkillCategory.choices,
        default=SkillCategory.OTHER,
        help_text=_('Skill category')
    )
    
    # Skill Information
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class or identifier')
    )
    
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text=_('Color code for the skill')
    )
    
    # Usage Statistics
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of users with this skill')
    )
    
    job_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of jobs requiring this skill')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the skill is active')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the skill is verified')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['usage_count']),
            models.Index(fields=['job_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def increment_usage_count(self):
        """Increment the usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def decrement_usage_count(self):
        """Decrement the usage count."""
        if self.usage_count > 0:
            self.usage_count -= 1
            self.save(update_fields=['usage_count'])
    
    def increment_job_count(self):
        """Increment the job count."""
        self.job_count += 1
        self.save(update_fields=['job_count'])
    
    def decrement_job_count(self):
        """Decrement the job count."""
        if self.job_count > 0:
            self.job_count -= 1
            self.save(update_fields=['job_count'])
    
    @classmethod
    def get_popular_skills(cls, limit=10):
        """Get the most popular skills."""
        return cls.objects.filter(
            is_active=True
        ).order_by('-usage_count')[:limit]
    
    @classmethod
    def get_skills_by_category(cls, category):
        """Get skills by category."""
        return cls.objects.filter(
            category=category,
            is_active=True
        ).order_by('name')


class UserSkill(models.Model):
    """
    User skills with proficiency levels and verification.
    """
    class ProficiencyLevel(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')
        EXPERT = 'expert', _('Expert')
    
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = 'unverified', _('Unverified')
        PENDING = 'pending', _('Pending Verification')
        VERIFIED = 'verified', _('Verified')
        REJECTED = 'rejected', _('Rejected')
    
    # User and Skill
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_skills',
        help_text=_('User who has this skill')
    )
    
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_skills',
        help_text=_('Skill that the user has')
    )
    
    # Proficiency and Experience
    proficiency_level = models.CharField(
        max_length=20,
        choices=ProficiencyLevel.choices,
        default=ProficiencyLevel.BEGINNER,
        help_text=_('User proficiency level in this skill')
    )
    
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Years of experience with this skill')
    )
    
    # Verification
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
        help_text=_('Verification status of the skill')
    )
    
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When the skill was verified')
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verified_skills',
        help_text=_('User who verified this skill')
    )
    
    # Additional Information
    description = models.TextField(
        blank=True,
        help_text=_('User description of their experience with this skill')
    )
    
    portfolio_links = models.JSONField(
        default=list,
        help_text=_('Links to portfolio items demonstrating this skill')
    )
    
    certifications = models.JSONField(
        default=list,
        help_text=_('List of certifications for this skill')
    )
    
    # Endorsements
    endorsement_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of endorsements for this skill')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Skill')
        verbose_name_plural = _('User Skills')
        unique_together = ['user', 'skill']
        ordering = ['-proficiency_level', '-endorsement_count']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['skill']),
            models.Index(fields=['proficiency_level']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['endorsement_count']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.get_proficiency_level_display()})"
    
    def save(self, *args, **kwargs):
        """Update skill usage count when user skill is saved."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.skill.increment_usage_count()
    
    def delete(self, *args, **kwargs):
        """Decrement skill usage count when user skill is deleted."""
        self.skill.decrement_usage_count()
        super().delete(*args, **kwargs)
    
    def verify_skill(self, verified_by_user):
        """Verify the user skill."""
        from django.utils import timezone
        self.verification_status = self.VerificationStatus.VERIFIED
        self.verified_at = timezone.now()
        self.verified_by = verified_by_user
        self.save(update_fields=['verification_status', 'verified_at', 'verified_by'])
    
    def reject_verification(self, verified_by_user):
        """Reject the skill verification."""
        from django.utils import timezone
        self.verification_status = self.VerificationStatus.REJECTED
        self.verified_at = timezone.now()
        self.verified_by = verified_by_user
        self.save(update_fields=['verification_status', 'verified_at', 'verified_by'])
    
    @property
    def is_verified(self):
        """Check if the skill is verified."""
        return self.verification_status == self.VerificationStatus.VERIFIED
    
    @property
    def is_expert_level(self):
        """Check if the skill is at expert level."""
        return self.proficiency_level == self.ProficiencyLevel.EXPERT
    
    @property
    def is_advanced_or_expert(self):
        """Check if the skill is at advanced or expert level."""
        return self.proficiency_level in [
            self.ProficiencyLevel.ADVANCED,
            self.ProficiencyLevel.EXPERT
        ] 
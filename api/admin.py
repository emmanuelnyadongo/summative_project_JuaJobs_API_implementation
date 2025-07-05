from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Job, JobCategory, JobApplication, Payment, PaymentMethod,
    Review, Notification, Location, Skill, UserSkill
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model."""
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'user_type',
        'is_verified', 'is_active_worker', 'country', 'city',
        'average_rating', 'total_reviews', 'created_at'
    ]
    list_filter = [
        'user_type', 'is_verified', 'is_active_worker', 'is_active',
        'country', 'city', 'gender', 'created_at'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    readonly_fields = ['total_earnings', 'total_spent', 'average_rating', 'total_reviews']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'profile_picture', 'date_of_birth', 'gender'
            )
        }),
        ('Location', {'fields': ('country', 'city', 'address')}),
        ('Account Type', {'fields': ('user_type', 'is_verified', 'is_active_worker')}),
        ('Worker Info', {
            'fields': ('hourly_rate', 'bio', 'years_of_experience'),
            'classes': ('collapse',)
        }),
        ('Client Info', {
            'fields': ('company_name', 'company_description'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('total_earnings', 'total_spent'),
            'classes': ('collapse',)
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('notification_preferences', 'language_preference'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    """Admin for JobCategory model."""
    list_display = ['name', 'description', 'is_active', 'job_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Job Count'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin for Job model."""
    list_display = [
        'title', 'client', 'category', 'job_type', 'status',
        'budget_range', 'is_remote', 'is_featured', 'is_urgent',
        'views_count', 'applications_count', 'created_at'
    ]
    list_filter = [
        'status', 'job_type', 'experience_level', 'category',
        'is_remote', 'is_featured', 'is_urgent', 'created_at'
    ]
    search_fields = ['title', 'description', 'client__username', 'location']
    ordering = ['-created_at']
    readonly_fields = ['views_count', 'applications_count', 'created_at', 'published_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'client')
        }),
        ('Job Details', {
            'fields': (
                'job_type', 'experience_level', 'budget_min', 'budget_max',
                'hourly_rate', 'estimated_hours'
            )
        }),
        ('Requirements', {
            'fields': ('required_skills', 'preferred_skills')
        }),
        ('Location & Timing', {
            'fields': (
                'is_remote', 'location', 'latitude', 'longitude',
                'deadline', 'start_date'
            )
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_worker')
        }),
        ('Metrics', {
            'fields': ('views_count', 'applications_count'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('attachments', 'tags', 'is_featured', 'is_urgent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Admin for JobApplication model."""
    list_display = [
        'job', 'worker', 'status', 'proposed_rate',
        'estimated_duration', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['job__title', 'worker__username', 'cover_letter']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin for PaymentMethod model."""
    list_display = [
        'user', 'payment_type', 'provider', 'account_name',
        'is_default', 'is_verified', 'created_at'
    ]
    list_filter = ['payment_type', 'provider', 'is_default', 'is_verified', 'created_at']
    search_fields = ['user__username', 'account_name', 'account_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model."""
    list_display = [
        'payment_id', 'amount', 'currency', 'payment_type',
        'status', 'payer', 'payee', 'created_at'
    ]
    list_filter = ['status', 'payment_type', 'currency', 'created_at']
    search_fields = ['payment_id', 'external_transaction_id', 'payer__username', 'payee__username']
    ordering = ['-created_at']
    readonly_fields = [
        'payment_id', 'external_transaction_id', 'platform_fee',
        'net_amount', 'created_at', 'updated_at', 'processed_at'
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model."""
    list_display = [
        'reviewer', 'reviewed_user', 'job', 'rating',
        'review_type', 'is_verified', 'has_response', 'created_at'
    ]
    list_filter = ['rating', 'review_type', 'is_verified', 'is_public', 'created_at']
    search_fields = ['reviewer__username', 'reviewed_user__username', 'job__title', 'title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'response_date']
    
    def has_response(self, obj):
        return bool(obj.response)
    has_response.boolean = True
    has_response.short_description = 'Has Response'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model."""
    list_display = [
        'user', 'notification_type', 'title', 'priority',
        'is_read', 'is_sent', 'created_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'is_sent', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'read_at', 'sent_at']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin for Location model."""
    list_display = [
        'name', 'location_type', 'parent', 'country_code',
        'population', 'is_active', 'created_at'
    ]
    list_filter = ['location_type', 'country_code', 'is_active', 'created_at']
    search_fields = ['name', 'country_code']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin for Skill model."""
    list_display = [
        'name', 'category', 'usage_count', 'job_count',
        'is_active', 'is_verified', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'is_verified', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['usage_count', 'job_count', 'created_at', 'updated_at']


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """Admin for UserSkill model."""
    list_display = [
        'user', 'skill', 'proficiency_level', 'verification_status',
        'endorsement_count', 'created_at'
    ]
    list_filter = [
        'proficiency_level', 'verification_status', 'skill__category', 'created_at'
    ]
    search_fields = ['user__username', 'skill__name', 'description']
    ordering = ['-created_at']
    readonly_fields = [
        'verification_status', 'verified_at', 'verified_by',
        'endorsement_count', 'created_at', 'updated_at'
    ]


# Customize admin site
admin.site.site_header = "JuaJobs API Administration"
admin.site.site_title = "JuaJobs Admin"
admin.site.index_title = "Welcome to JuaJobs API Administration" 
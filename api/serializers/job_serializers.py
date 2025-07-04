from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models import Job, JobCategory, JobApplication, User


class JobCategorySerializer(serializers.ModelSerializer):
    """Serializer for job categories."""
    
    job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobCategory
        fields = [
            'id', 'name', 'description', 'icon', 'is_active',
            'job_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'job_count', 'created_at', 'updated_at']
    
    def get_job_count(self, obj):
        return obj.jobs.filter(status='open').count()


class JobSerializer(serializers.ModelSerializer):
    """Basic job serializer."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name_or_username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)
    experience_level_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    budget_range = serializers.CharField(read_only=True)
    time_since_posted = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'client', 'client_name', 'job_type', 'job_type_display',
            'experience_level', 'experience_level_display', 'budget_min',
            'budget_max', 'hourly_rate', 'estimated_hours', 'budget_range',
            'required_skills', 'preferred_skills', 'is_remote', 'location',
            'latitude', 'longitude', 'deadline', 'start_date', 'status',
            'status_display', 'assigned_worker', 'views_count',
            'applications_count', 'created_at', 'published_at',
            'attachments', 'tags', 'is_featured', 'is_urgent',
            'time_since_posted'
        ]
        read_only_fields = [
            'id', 'client', 'assigned_worker', 'views_count',
            'applications_count', 'created_at', 'published_at'
        ]
    
    def get_time_since_posted(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class JobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new jobs."""
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'category', 'job_type',
            'experience_level', 'budget_min', 'budget_max',
            'hourly_rate', 'estimated_hours', 'required_skills',
            'preferred_skills', 'is_remote', 'location', 'latitude',
            'longitude', 'deadline', 'start_date', 'attachments', 'tags'
        ]
    
    def validate(self, attrs):
        # Ensure client can only post jobs
        user = self.context['request'].user
        if not user.is_client:
            raise serializers.ValidationError(
                "Only clients can post jobs."
            )
        
        # Validate budget range
        if attrs.get('budget_min') and attrs.get('budget_max'):
            if attrs['budget_min'] > attrs['budget_max']:
                raise serializers.ValidationError(
                    "Minimum budget cannot be greater than maximum budget."
                )
        
        # Validate hourly rate for hourly jobs
        if attrs.get('job_type') == 'hourly' and not attrs.get('hourly_rate'):
            raise serializers.ValidationError(
                "Hourly rate is required for hourly jobs."
            )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class JobUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating jobs."""
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'category', 'job_type',
            'experience_level', 'budget_min', 'budget_max',
            'hourly_rate', 'estimated_hours', 'required_skills',
            'preferred_skills', 'is_remote', 'location', 'latitude',
            'longitude', 'deadline', 'start_date', 'attachments', 'tags'
        ]
    
    def validate(self, attrs):
        # Ensure only the job owner can update
        user = self.context['request'].user
        if self.instance.client != user:
            raise serializers.ValidationError(
                "You can only update your own jobs."
            )
        
        # Prevent updates if job is in progress or completed
        if self.instance.status in ['in_progress', 'completed']:
            raise serializers.ValidationError(
                "Cannot update job that is in progress or completed."
            )
        
        return attrs


class JobDetailSerializer(JobSerializer):
    """Detailed job serializer with additional information."""
    
    client_profile = serializers.SerializerMethodField()
    assigned_worker_profile = serializers.SerializerMethodField()
    applications_count = serializers.IntegerField(read_only=True)
    user_has_applied = serializers.SerializerMethodField()
    
    class Meta(JobSerializer.Meta):
        fields = JobSerializer.Meta.fields + [
            'client_profile', 'assigned_worker_profile',
            'user_has_applied'
        ]
    
    def get_client_profile(self, obj):
        from .user_serializers import UserSerializer
        return UserSerializer(obj.client).data
    
    def get_assigned_worker_profile(self, obj):
        if obj.assigned_worker:
            from .user_serializers import UserSerializer
            return UserSerializer(obj.assigned_worker).data
        return None
    
    def get_user_has_applied(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and user.is_worker:
            return obj.applications.filter(worker=user).exists()
        return False


class JobApplicationSerializer(serializers.ModelSerializer):
    """Basic job application serializer."""
    
    worker_name = serializers.CharField(source='worker.get_full_name_or_username', read_only=True)
    worker_rating = serializers.DecimalField(source='worker.average_rating', read_only=True, max_digits=3, decimal_places=2)
    worker_reviews_count = serializers.IntegerField(source='worker.total_reviews', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    time_since_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'worker', 'worker_name', 'worker_rating',
            'worker_reviews_count', 'cover_letter', 'proposed_rate',
            'estimated_duration', 'status', 'status_display',
            'client_message', 'created_at', 'updated_at',
            'attachments', 'time_since_applied'
        ]
        read_only_fields = [
            'id', 'worker', 'status', 'client_message',
            'created_at', 'updated_at'
        ]
    
    def get_time_since_applied(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job applications."""
    
    class Meta:
        model = JobApplication
        fields = [
            'job', 'cover_letter', 'proposed_rate',
            'estimated_duration', 'attachments'
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Ensure only workers can apply
        if not user.is_worker:
            raise serializers.ValidationError(
                "Only workers can apply for jobs."
            )
        
        job = attrs['job']
        
        # Check if job is open
        if job.status != 'open':
            raise serializers.ValidationError(
                "This job is not open for applications."
            )
        
        # Check if user has already applied
        if JobApplication.objects.filter(job=job, worker=user).exists():
            raise serializers.ValidationError(
                "You have already applied for this job."
            )
        
        # Validate proposed rate
        if attrs.get('proposed_rate'):
            if job.job_type == 'hourly':
                if attrs['proposed_rate'] <= 0:
                    raise serializers.ValidationError(
                        "Proposed hourly rate must be greater than 0."
                    )
            else:
                if attrs['proposed_rate'] < job.budget_min or attrs['proposed_rate'] > job.budget_max:
                    raise serializers.ValidationError(
                        f"Proposed rate must be between {job.budget_min} and {job.budget_max}."
                    )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['worker'] = self.context['request'].user
        return super().create(validated_data)


class JobApplicationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating job applications."""
    
    class Meta:
        model = JobApplication
        fields = [
            'cover_letter', 'proposed_rate', 'estimated_duration',
            'attachments'
        ]
    
    def validate(self, attrs):
        # Ensure only the applicant can update
        user = self.context['request'].user
        if self.instance.worker != user:
            raise serializers.ValidationError(
                "You can only update your own applications."
            )
        
        # Prevent updates if application is not pending
        if self.instance.status != 'pending':
            raise serializers.ValidationError(
                "Cannot update application that is not pending."
            )
        
        return attrs


class JobApplicationResponseSerializer(serializers.ModelSerializer):
    """Serializer for client responses to job applications."""
    
    class Meta:
        model = JobApplication
        fields = ['status', 'client_message']
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Ensure only the job owner can respond
        if self.instance.job.client != user:
            raise serializers.ValidationError(
                "You can only respond to applications for your own jobs."
            )
        
        # Validate status transitions
        if self.instance.status != 'pending':
            raise serializers.ValidationError(
                "Can only respond to pending applications."
            )
        
        return attrs
    
    def update(self, instance, validated_data):
        # If accepting the application, assign the worker to the job
        if validated_data.get('status') == 'accepted':
            instance.job.assigned_worker = instance.worker
            instance.job.status = 'in_progress'
            instance.job.save()
        
        return super().update(instance, validated_data)


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search parameters."""
    
    q = serializers.CharField(required=False, help_text="Search query")
    category = serializers.IntegerField(required=False, help_text="Category ID")
    job_type = serializers.ChoiceField(choices=Job.JobType.choices, required=False)
    experience_level = serializers.ChoiceField(choices=Job.ExperienceLevel.choices, required=False)
    min_budget = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_budget = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    is_remote = serializers.BooleanField(required=False)
    location = serializers.CharField(required=False)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    featured = serializers.BooleanField(required=False)
    urgent = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=[
            'created_at', '-created_at', 'budget_min', '-budget_min',
            'views_count', '-views_count', 'applications_count', '-applications_count'
        ],
        required=False,
        default='-created_at'
    ) 
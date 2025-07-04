from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ..models import Review, User, Job


class ReviewSerializer(serializers.ModelSerializer):
    """Basic review serializer."""
    
    reviewer_name = serializers.CharField(source='reviewer.get_full_name_or_username', read_only=True)
    reviewed_user_name = serializers.CharField(source='reviewed_user.get_full_name_or_username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    time_since_review = serializers.SerializerMethodField()
    average_specific_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewed_user',
            'reviewed_user_name', 'job', 'job_title', 'review_type',
            'review_type_display', 'rating', 'title', 'comment',
            'communication_rating', 'quality_rating', 'timeliness_rating',
            'professionalism_rating', 'average_specific_rating',
            'is_public', 'is_verified', 'response', 'response_date',
            'created_at', 'updated_at', 'time_since_review'
        ]
        read_only_fields = [
            'id', 'reviewer', 'reviewed_user', 'job', 'is_verified',
            'response_date', 'created_at', 'updated_at'
        ]
    
    def get_time_since_review(self, obj):
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
    
    def get_average_specific_rating(self, obj):
        return obj.get_average_specific_rating()


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = [
            'reviewed_user', 'job', 'review_type', 'rating', 'title',
            'comment', 'communication_rating', 'quality_rating',
            'timeliness_rating', 'professionalism_rating'
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        job = attrs.get('job')
        reviewed_user = attrs.get('reviewed_user')
        review_type = attrs.get('review_type')
        
        # Ensure user can only review for completed jobs they were involved in
        if job.status != 'completed':
            raise serializers.ValidationError(
                "Can only review completed jobs."
            )
        
        # Validate review type and user relationship
        if review_type == 'client_to_worker':
            if job.client != user:
                raise serializers.ValidationError(
                    "Only the job client can review the worker."
                )
            if job.assigned_worker != reviewed_user:
                raise serializers.ValidationError(
                    "Can only review the worker assigned to the job."
                )
        elif review_type == 'worker_to_client':
            if job.assigned_worker != user:
                raise serializers.ValidationError(
                    "Only the assigned worker can review the client."
                )
            if job.client != reviewed_user:
                raise serializers.ValidationError(
                    "Can only review the job client."
                )
        
        # Check if user has already reviewed this person for this job
        if Review.objects.filter(
            reviewer=user,
            reviewed_user=reviewed_user,
            job=job,
            review_type=review_type
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this user for this job."
            )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews."""
    
    class Meta:
        model = Review
        fields = [
            'title', 'comment', 'communication_rating', 'quality_rating',
            'timeliness_rating', 'professionalism_rating'
        ]
    
    def validate(self, attrs):
        # Ensure only the reviewer can update
        user = self.context['request'].user
        if self.instance.reviewer != user:
            raise serializers.ValidationError(
                "You can only update your own reviews."
            )
        
        # Prevent updates after a certain time (e.g., 30 days)
        from django.utils import timezone
        from datetime import timedelta
        
        if self.instance.created_at < timezone.now() - timedelta(days=30):
            raise serializers.ValidationError(
                "Cannot update reviews older than 30 days."
            )
        
        return attrs


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for responding to reviews."""
    
    class Meta:
        model = Review
        fields = ['response']
    
    def validate(self, attrs):
        # Ensure only the reviewed user can respond
        user = self.context['request'].user
        if self.instance.reviewed_user != user:
            raise serializers.ValidationError(
                "You can only respond to reviews about you."
            )
        
        # Check if already responded
        if self.instance.response:
            raise serializers.ValidationError(
                "You have already responded to this review."
            )
        
        return attrs


class ReviewListSerializer(serializers.ModelSerializer):
    """Serializer for listing reviews with pagination."""
    
    reviewer_name = serializers.CharField(source='reviewer.get_full_name_or_username', read_only=True)
    reviewer_avatar = serializers.CharField(source='reviewer.profile_picture', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    time_since_review = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer_name', 'reviewer_avatar', 'job_title',
            'rating', 'title', 'comment', 'review_type', 'is_verified',
            'response', 'created_at', 'time_since_review'
        ]
        read_only_fields = fields
    
    def get_time_since_review(self, obj):
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


class UserReviewStatsSerializer(serializers.Serializer):
    """Serializer for user review statistics."""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    rating_distribution = serializers.DictField()
    recent_reviews = serializers.ListField()
    
    def to_representation(self, instance):
        # Calculate rating distribution
        reviews = instance.reviews_received.all()
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        # Get recent reviews
        recent_reviews = reviews.order_by('-created_at')[:5]
        recent_reviews_data = ReviewListSerializer(recent_reviews, many=True).data
        
        return {
            'total_reviews': reviews.count(),
            'average_rating': instance.average_rating,
            'rating_distribution': rating_distribution,
            'recent_reviews': recent_reviews_data
        }


class ReviewFilterSerializer(serializers.Serializer):
    """Serializer for review filtering parameters."""
    
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    review_type = serializers.ChoiceField(choices=Review.ReviewType.choices, required=False)
    verified_only = serializers.BooleanField(required=False)
    has_response = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['created_at', '-created_at', 'rating', '-rating'],
        required=False,
        default='-created_at'
    ) 
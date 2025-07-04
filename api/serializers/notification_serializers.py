from rest_framework import serializers
from ..models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Basic notification serializer."""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'is_read', 'is_sent', 'related_job_id', 'related_user_id',
            'related_payment_id', 'data', 'created_at', 'read_at',
            'sent_at', 'time_since_created'
        ]
        read_only_fields = [
            'id', 'user', 'notification_type', 'title', 'message',
            'priority', 'is_sent', 'related_job_id', 'related_user_id',
            'related_payment_id', 'data', 'created_at', 'sent_at'
        ]
    
    def get_time_since_created(self, obj):
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


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification status."""
    
    class Meta:
        model = Notification
        fields = ['is_read']
    
    def validate(self, attrs):
        # Ensure only the notification owner can update
        user = self.context['request'].user
        if self.instance.user != user:
            raise serializers.ValidationError(
                "You can only update your own notifications."
            )
        return attrs


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer for listing notifications with pagination."""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'is_read', 'related_job_id', 'related_user_id',
            'related_payment_id', 'created_at', 'time_since_created'
        ]
        read_only_fields = fields
    
    def get_time_since_created(self, obj):
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


class NotificationFilterSerializer(serializers.Serializer):
    """Serializer for notification filtering parameters."""
    
    notification_type = serializers.ChoiceField(choices=Notification.NotificationType.choices, required=False)
    is_read = serializers.BooleanField(required=False)
    priority = serializers.ChoiceField(choices=Notification.Priority.choices, required=False)
    sort_by = serializers.ChoiceField(
        choices=['created_at', '-created_at', 'priority', '-priority'],
        required=False,
        default='-created_at'
    ) 
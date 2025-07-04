from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for general use."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone_number', 'profile_picture', 'date_of_birth',
            'gender', 'country', 'city', 'address', 'is_verified',
            'is_active_worker', 'hourly_rate', 'bio', 'years_of_experience',
            'company_name', 'company_description', 'total_earnings',
            'total_spent', 'average_rating', 'total_reviews',
            'created_at', 'last_active'
        ]
        read_only_fields = [
            'id', 'total_earnings', 'total_spent', 'average_rating',
            'total_reviews', 'created_at', 'last_active'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'first_name',
            'last_name', 'user_type', 'phone_number', 'date_of_birth',
            'gender', 'country', 'city', 'address'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'profile_picture',
            'date_of_birth', 'gender', 'country', 'city', 'address',
            'hourly_rate', 'bio', 'years_of_experience', 'company_name',
            'company_description', 'notification_preferences',
            'language_preference'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user profile serializer."""
    
    user_type_display = serializers.CharField(
        source='get_user_type_display',
        read_only=True
    )
    
    gender_display = serializers.CharField(
        source='get_gender_display',
        read_only=True
    )
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'user_type_display', 'phone_number', 'profile_picture',
            'date_of_birth', 'gender', 'gender_display', 'country', 'city',
            'address', 'is_verified', 'is_active_worker', 'hourly_rate',
            'bio', 'years_of_experience', 'company_name', 'company_description',
            'total_earnings', 'total_spent', 'average_rating', 'total_reviews',
            'created_at', 'last_active', 'notification_preferences',
            'language_preference'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'user_type', 'is_verified',
            'total_earnings', 'total_spent', 'average_rating',
            'total_reviews', 'created_at', 'last_active'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name_or_username()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'first_name',
            'last_name', 'user_type', 'phone_number', 'country', 'city'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'user_type': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".'
            )
        
        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Old password is not correct.'
            )
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'No user found with this email address.'
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password2 = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class UserStatsSerializer(serializers.ModelSerializer):
    """Serializer for user statistics."""
    
    total_jobs_posted = serializers.SerializerMethodField()
    total_jobs_completed = serializers.SerializerMethodField()
    total_applications = serializers.SerializerMethodField()
    total_applications_accepted = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'user_type', 'total_earnings', 'total_spent',
            'average_rating', 'total_reviews', 'total_jobs_posted',
            'total_jobs_completed', 'total_applications',
            'total_applications_accepted', 'created_at'
        ]
        read_only_fields = fields
    
    def get_total_jobs_posted(self, obj):
        if obj.is_client:
            return obj.posted_jobs.count()
        return 0
    
    def get_total_jobs_completed(self, obj):
        if obj.is_worker:
            return obj.assigned_jobs.filter(status='completed').count()
        return 0
    
    def get_total_applications(self, obj):
        if obj.is_worker:
            return obj.job_applications.count()
        return 0
    
    def get_total_applications_accepted(self, obj):
        if obj.is_worker:
            return obj.job_applications.filter(status='accepted').count()
        return 0 
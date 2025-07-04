from rest_framework import serializers
from ..models import Skill, UserSkill


class SkillSerializer(serializers.ModelSerializer):
    """Basic skill serializer."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'icon', 'color', 'usage_count', 'job_count', 'is_active',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'usage_count', 'job_count', 'is_verified',
            'created_at', 'updated_at'
        ]


class UserSkillSerializer(serializers.ModelSerializer):
    """Basic user skill serializer."""
    
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    skill_category_display = serializers.CharField(source='skill.get_category_display', read_only=True)
    proficiency_level_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill', 'skill_name', 'skill_category', 'skill_category_display',
            'proficiency_level', 'proficiency_level_display', 'years_of_experience',
            'verification_status', 'verification_status_display', 'verified_at',
            'verified_by', 'description', 'portfolio_links', 'certifications',
            'endorsement_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'skill', 'verification_status', 'verified_at',
            'verified_by', 'endorsement_count', 'created_at', 'updated_at'
        ]


class UserSkillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user skills."""
    
    class Meta:
        model = UserSkill
        fields = [
            'skill', 'proficiency_level', 'years_of_experience',
            'description', 'portfolio_links', 'certifications'
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        skill = attrs.get('skill')
        
        # Check if user already has this skill
        if UserSkill.objects.filter(user=user, skill=skill).exists():
            raise serializers.ValidationError(
                "You already have this skill listed."
            )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserSkillUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user skills."""
    
    class Meta:
        model = UserSkill
        fields = [
            'proficiency_level', 'years_of_experience', 'description',
            'portfolio_links', 'certifications'
        ]
    
    def validate(self, attrs):
        # Ensure only the skill owner can update
        user = self.context['request'].user
        if self.instance.user != user:
            raise serializers.ValidationError(
                "You can only update your own skills."
            )
        return attrs


class SkillSearchSerializer(serializers.Serializer):
    """Serializer for skill search parameters."""
    
    q = serializers.CharField(required=False, help_text="Search query")
    category = serializers.ChoiceField(choices=Skill.SkillCategory.choices, required=False)
    is_active = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['name', 'usage_count', '-usage_count', 'job_count', '-job_count'],
        required=False,
        default='name'
    )


class UserSkillFilterSerializer(serializers.Serializer):
    """Serializer for user skill filtering parameters."""
    
    proficiency_level = serializers.ChoiceField(choices=UserSkill.ProficiencyLevel.choices, required=False)
    verification_status = serializers.ChoiceField(choices=UserSkill.VerificationStatus.choices, required=False)
    skill_category = serializers.ChoiceField(choices=Skill.SkillCategory.choices, required=False)
    sort_by = serializers.ChoiceField(
        choices=['proficiency_level', '-proficiency_level', 'endorsement_count', '-endorsement_count'],
        required=False,
        default='-proficiency_level'
    ) 
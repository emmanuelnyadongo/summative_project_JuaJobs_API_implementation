from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from ..models import Skill, UserSkill, User
from ..serializers import (
    SkillSerializer,
    UserSkillSerializer,
    UserSkillCreateSerializer,
)
from ..permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class SkillViewSet(viewsets.ModelViewSet):
    """
    Skill ViewSet for managing skills.
    
    list: GET /api/skills/
    create: POST /api/skills/ (admin only)
    retrieve: GET /api/skills/{id}/
    update: PUT /api/skills/{id}/ (admin only)
    partial_update: PATCH /api/skills/{id}/ (admin only)
    destroy: DELETE /api/skills/{id}/ (admin only)
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_verified']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'usage_count', 'job_count', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category if specified
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by active status
        active_only = self.request.query_params.get('active_only', 'true').lower() == 'true'
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        # Filter by minimum usage count
        min_usage = self.request.query_params.get('min_usage')
        if min_usage:
            queryset = queryset.filter(usage_count__gte=min_usage)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular skills."""
        skills = self.get_queryset().order_by('-usage_count')[:10]
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all skill categories with counts."""
        categories = Skill.objects.values('category').annotate(
            count=Count('id')
        ).order_by('category')
        return Response(categories)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users who have this skill."""
        skill = self.get_object()
        users = User.objects.filter(user_skills__skill=skill).distinct()
        from ..serializers import UserSerializer
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserSkillViewSet(viewsets.ModelViewSet):
    """
    UserSkill ViewSet for managing user skills.
    
    list: GET /api/user-skills/
    create: POST /api/user-skills/
    retrieve: GET /api/user-skills/{id}/
    update: PUT /api/user-skills/{id}/
    partial_update: PATCH /api/user-skills/{id}/
    destroy: DELETE /api/user-skills/{id}/
    """
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['proficiency_level', 'verification_status', 'skill__category']
    search_fields = ['skill__name', 'description']
    ordering_fields = ['proficiency_level', 'endorsement_count', 'created_at']
    ordering = ['-proficiency_level']
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserSkillCreateSerializer
        return UserSkillSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_skills(self, request):
        """Get current user's skills."""
        skills = self.get_queryset()
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get user skills grouped by category."""
        skills = self.get_queryset().select_related('skill')
        categories = {}
        
        for user_skill in skills:
            category = user_skill.skill.get_category_display()
            if category not in categories:
                categories[category] = []
            categories[category].append(UserSkillSerializer(user_skill).data)
        
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def endorse(self, request, pk=None):
        """Endorse a user skill."""
        user_skill = self.get_object()
        
        # Check if user can endorse (not their own skill)
        if user_skill.user == request.user:
            return Response(
                {'error': 'You cannot endorse your own skill.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In a real implementation, you would track who endorsed what
        # For now, we'll just increment the endorsement count
        user_skill.endorsement_count += 1
        user_skill.save()
        
        serializer = self.get_serializer(user_skill)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get skill recommendations for the current user."""
        user = request.user
        
        # Get skills the user doesn't have
        user_skill_ids = user.user_skills.values_list('skill_id', flat=True)
        recommended_skills = Skill.objects.filter(
            is_active=True
        ).exclude(
            id__in=user_skill_ids
        ).order_by('-usage_count')[:10]
        
        serializer = SkillSerializer(recommended_skills, many=True)
        return Response(serializer.data) 
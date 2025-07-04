from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import User
from ..serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    UserStatsSerializer,
)
from ..permissions import IsOwnerOrReadOnly, ReadOnlyIfNotOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    User ViewSet for managing users.
    
    list: GET /api/users/
    create: POST /api/users/
    retrieve: GET /api/users/{id}/
    update: PUT /api/users/{id}/
    partial_update: PATCH /api/users/{id}/
    destroy: DELETE /api/users/{id}/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_verified', 'is_active_worker', 'country', 'city']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'company_name']
    ordering_fields = ['created_at', 'last_active', 'average_rating', 'total_earnings']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserProfileSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user type if specified
        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Filter by rating if specified
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=min_rating)
        
        # Filter by hourly rate if specified
        min_rate = self.request.query_params.get('min_hourly_rate')
        if min_rate:
            queryset = queryset.filter(hourly_rate__gte=min_rate)
        
        max_rate = self.request.query_params.get('max_hourly_rate')
        if max_rate:
            queryset = queryset.filter(hourly_rate__lte=max_rate)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get detailed user profile."""
        user = self.get_object()
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get user statistics."""
        user = self.get_object()
        serializer = UserStatsSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def workers(self, request):
        """Get all workers."""
        workers = User.objects.filter(user_type='worker', is_active_worker=True)
        page = self.paginate_queryset(workers)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(workers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def clients(self, request):
        """Get all clients."""
        clients = User.objects.filter(user_type='client')
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(clients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a user (admin only)."""
        user = self.get_object()
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can verify users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_verified = True
        user.save()
        return Response({'message': 'User verified successfully.'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user (admin only)."""
        user = self.get_object()
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can deactivate users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully.'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view for current user.
    
    GET /api/users/profile/
    PUT /api/users/profile/
    PATCH /api/users/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserStatsView(generics.RetrieveAPIView):
    """
    User statistics view.
    
    GET /api/users/{id}/stats/
    """
    serializer_class = UserStatsSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    
    def get_object(self):
        user_id = self.kwargs.get('pk')
        if user_id == 'me':
            return self.request.user
        return super().get_object() 
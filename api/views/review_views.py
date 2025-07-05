from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import Review, User
from ..serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewResponseSerializer,
    ReviewListSerializer,
    UserReviewStatsSerializer,
)
from ..permissions import IsReviewOwnerOrReviewed


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Review ViewSet for managing reviews.
    
    list: GET /api/reviews/
    create: POST /api/reviews/
    retrieve: GET /api/reviews/{id}/
    update: PUT /api/reviews/{id}/
    partial_update: PATCH /api/reviews/{id}/
    destroy: DELETE /api/reviews/{id}/
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrReviewed]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['rating', 'review_type', 'is_verified']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user role
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(reviewer=self.request.user) | Q(reviewed_user=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the reviewer when creating a review."""
        serializer.save(reviewer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews."""
        reviews = Review.objects.filter(reviewer=request.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def reviews_about_me(self, request):
        """Get reviews about current user."""
        reviews = Review.objects.filter(reviewed_user=request.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewResponseView(generics.UpdateAPIView):
    """
    Review response view for responding to reviews.
    
    PATCH /api/reviews/{id}/respond/
    """
    queryset = Review.objects.all()
    serializer_class = ReviewResponseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(reviewed_user=self.request.user)


class UserReviewStatsView(generics.RetrieveAPIView):
    """
    User review statistics view.
    
    GET /api/users/{id}/review-stats/
    """
    serializer_class = UserReviewStatsSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all() 
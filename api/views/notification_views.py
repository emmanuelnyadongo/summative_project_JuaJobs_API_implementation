from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import Notification
from ..serializers import (
    NotificationSerializer,
    NotificationUpdateSerializer,
    NotificationListSerializer,
)
from ..permissions import IsNotificationOwner


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Notification ViewSet for managing notifications.
    
    list: GET /api/notifications/
    retrieve: GET /api/notifications/{id}/
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsNotificationOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification_type', 'is_read', 'priority']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read.'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class NotificationMarkReadView(generics.UpdateAPIView):
    """
    Notification mark as read view.
    
    PATCH /api/notifications/{id}/mark-read/
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user) 
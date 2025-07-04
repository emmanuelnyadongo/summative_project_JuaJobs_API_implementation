from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Location
from ..serializers import (
    LocationSerializer,
    LocationTreeSerializer,
    LocationSearchSerializer,
)


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Location ViewSet for managing locations.
    
    list: GET /api/locations/
    retrieve: GET /api/locations/{id}/
    """
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location_type', 'country_code']
    search_fields = ['name']
    ordering_fields = ['name', 'population']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get children of a location."""
        location = self.get_object()
        children = location.children.filter(is_active=True)
        serializer = LocationSerializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ancestors(self, request, pk=None):
        """Get ancestors of a location."""
        location = self.get_object()
        ancestors = location.get_ancestors()
        serializer = LocationSerializer(ancestors, many=True)
        return Response(serializer.data)


class LocationTreeView(generics.ListAPIView):
    """
    Location tree view for hierarchical data.
    
    GET /api/locations/tree/
    """
    serializer_class = LocationTreeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Location.objects.filter(is_active=True, parent=None) 
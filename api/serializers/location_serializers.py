from rest_framework import serializers
from ..models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Basic location serializer."""
    
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'location_type', 'location_type_display',
            'latitude', 'longitude', 'parent', 'country_code',
            'timezone', 'population', 'is_active', 'full_path',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'children_count', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.children.count()


class LocationTreeSerializer(serializers.ModelSerializer):
    """Serializer for hierarchical location tree."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'location_type', 'latitude', 'longitude',
            'country_code', 'is_active', 'children'
        ]
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return LocationTreeSerializer(children, many=True).data


class LocationSearchSerializer(serializers.Serializer):
    """Serializer for location search parameters."""
    
    q = serializers.CharField(required=False, help_text="Search query")
    location_type = serializers.ChoiceField(choices=Location.LocationType.choices, required=False)
    country_code = serializers.CharField(required=False)
    parent_id = serializers.IntegerField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['name', 'population', '-population'],
        required=False,
        default='name'
    ) 
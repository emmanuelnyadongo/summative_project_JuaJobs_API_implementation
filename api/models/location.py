from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    """
    Location model for geographical data and location-based features.
    """
    class LocationType(models.TextChoices):
        COUNTRY = 'country', _('Country')
        STATE = 'state', _('State/Province')
        CITY = 'city', _('City')
        DISTRICT = 'district', _('District')
        NEIGHBORHOOD = 'neighborhood', _('Neighborhood')
    
    # Location Details
    name = models.CharField(
        max_length=200,
        help_text=_('Location name')
    )
    
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        help_text=_('Type of location')
    )
    
    # Geographical Coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('Location latitude')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('Location longitude')
    )
    
    # Hierarchical Structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        help_text=_('Parent location')
    )
    
    # Additional Information
    country_code = models.CharField(
        max_length=3,
        blank=True,
        help_text=_('ISO country code')
    )
    
    timezone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Timezone for this location')
    )
    
    population = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Population of the location')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the location is active')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ['name']
        unique_together = ['name', 'location_type', 'parent']
        indexes = [
            models.Index(fields=['location_type']),
            models.Index(fields=['country_code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.name}, {self.parent.name}"
        return self.name
    
    @property
    def full_path(self):
        """Get the full hierarchical path of the location."""
        path = [self.name]
        current = self.parent
        while current:
            path.append(current.name)
            current = current.parent
        return ', '.join(reversed(path))
    
    @property
    def coordinates(self):
        """Get coordinates as tuple."""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
    
    def get_children_recursive(self):
        """Get all children recursively."""
        children = list(self.children.all())
        for child in children:
            children.extend(child.get_children_recursive())
        return children
    
    def get_ancestors(self):
        """Get all ancestors of this location."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    @classmethod
    def get_by_coordinates(cls, lat, lng, radius_km=10):
        """Get locations within a radius of given coordinates."""
        # This is a simplified version. In production, you'd use PostGIS or similar
        # for proper geographical queries
        return cls.objects.filter(
            latitude__range=(lat - 0.1, lat + 0.1),
            longitude__range=(lng - 0.1, lng + 0.1),
            is_active=True
        )
    
    def distance_to(self, other_location):
        """Calculate distance to another location in kilometers."""
        if not (self.coordinates and other_location.coordinates):
            return None
        
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = self.coordinates
        lat2, lon2 = other_location.coordinates
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r 
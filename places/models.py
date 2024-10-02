from django.db import models
from django.core.exceptions import ValidationError
from core.base_models import BaseModel
from django_admin_geomap import GeoItem
from user_profile.models import UserProfile



class Category(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @property
    def is_subcategory(self):
        return self.parent is not None
    

class Building(BaseModel, GeoItem):
    user_profile = models.ForeignKey(
        UserProfile, related_name='user_building', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()
    is_food_establishment = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name="buildings")
    map_icon = models.ImageField(
        upload_to='images/map/icon/', blank=True, null=True)

    @property
    def geomap_longitude(self):
        return '' if self.longitude is None else str(self.longitude)

    @property
    def geomap_latitude(self):
        return '' if self.latitude is None else str(self.latitude)

    @property
    def geomap_popup_view(self):
        return "<strong>{}</strong>".format(str(self))

    @property
    def geomap_popup_edit(self):
        return self.geomap_popup_view

    @property
    def geomap_popup_common(self):
        return self.geomap_popup_view
    
    @property
    def geomap_icon(self):
        return self.default_icon
    
    class Meta:
        managed = True
        ordering = ['-updated_at',]
    
    def __str__(self):
        return f'{self.name}- {self.address}'


    def __str__(self):
        return self.name

    def clean(self):
        if not (-180 <= self.longitude <= 180):
            raise ValidationError('Longitude must be between -180 and 180.')
        if not (-90 <= self.latitude <= 90):
            raise ValidationError('Latitude must be between -90 and 90.')
        
class Rental(Building):
    num_bedrooms = models.IntegerField()
    num_bathrooms = models.IntegerField()
    kitchen = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    refrigerator = models.BooleanField(default=False)
    emergency_exit = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=25, null=True, blank=True)

    # New fields
    PROPERTY_CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('OLD', 'Old'),
    ]
    FURNITURE_CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('GOOD', 'Good'),
        ('USED', 'Used'),
    ]
    LEASE_TERM_CHOICES = [
        ('SHORT_TERM', 'Short-term'),
        ('LONG_TERM', 'Long-term'),
        ('MONTH_TO_MONTH', 'Month-to-month'),
    ]
    PROPERTY_TYPE_CHOICES = [
        ('APARTMENT', 'Apartment'),
        ('DORMITORY', 'Dormitory'),
        ('CONDOMINIUM', 'Condominium'),
    ]

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='APARTMENT')
    property_condition = models.CharField(max_length=10, choices=PROPERTY_CONDITION_CHOICES, default='GOOD')
    furniture_condition = models.CharField(max_length=10, choices=FURNITURE_CONDITION_CHOICES, default='GOOD')
    lease_term = models.CharField(max_length=20, choices=LEASE_TERM_CHOICES, default='LONG_TERM')

    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - Accommodation"


class FoodEstablishment(Building):
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return f"{self.name} - {self.cuisine_type}"


class BuildingPhoto(BaseModel):
    building = models.ForeignKey(Building, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='building_photos/')
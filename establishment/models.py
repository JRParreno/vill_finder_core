from django.db import models

from core.base_models import BaseModel
from user_profile.models import UserProfile
from django_admin_geomap import GeoItem
from django.core.exceptions import ValidationError

class BusinessCategory(BaseModel):
    name = models.CharField(max_length=150)


    class Meta:
        managed = True
        verbose_name = "Business Category"
        verbose_name_plural = "Business Categories"
        ordering = ['name',]
        
    def __str__(self):
        return self.name

class BusinessSubCategory(BaseModel):
    name = models.CharField(max_length=150)
    categories = models.ForeignKey(
        BusinessCategory, related_name='category', on_delete=models.CASCADE, null=True)

    class Meta:
        managed = True
        verbose_name = "Business Sub Category"
        verbose_name_plural = "Business Sub Categories"
        ordering = ['name',]
        
    def __str__(self):
        return f'{self.name} - {self.categories.name}'

class Business(BaseModel, GeoItem):
    user_profile = models.ForeignKey(
        UserProfile, related_name='user_shop', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField()
    address = models.CharField(max_length=150)
    longitude = models.FloatField()
    latitude = models.FloatField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    category = models.ManyToManyField(BusinessSubCategory)
    
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
        verbose_name = "Business"
        verbose_name_plural = "Business"
        ordering = ['-updated_at',]
    
    def __str__(self):
        return f'{self.name}- {self.address}'


class BusinessPhotos(BaseModel):
    business = models.ForeignKey(
        Business, related_name='business_photos', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='business-pictures/', blank=True, null=True)
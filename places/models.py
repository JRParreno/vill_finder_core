from django.db import models
from django.core.exceptions import ValidationError
from core.base_models import BaseModel
from django_admin_geomap import GeoItem
from user_profile.models import UserProfile
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

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
    name = models.CharField(max_length=255, unique=True)  # Ensure building names are unique
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()
    is_food_establishment = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name="buildings")
    map_icon = models.ImageField(upload_to='images/map/icon/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=50, null=True, blank=False)
    contact_number = models.CharField(max_length=25, null=True, blank=True)
    
    @property
    def geomap_longitude(self):
        return str(self.longitude)

    @property
    def geomap_latitude(self):
        return str(self.latitude)

    class Meta:
        managed = True
        ordering = ['-updated_at',]
    
    def __str__(self):
        return f'{self.name} - {self.address}'



class Rental(Building):
    kitchen = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    refrigerator = models.BooleanField(default=False)
    emergency_exit = models.BooleanField(default=False)
    num_bedrooms = models.PositiveIntegerField(default=0)  # Only positive integers
    num_bathrooms = models.PositiveIntegerField(default=0)  # Only positive integers
    available_bedrooms = models.PositiveIntegerField(default=0)  # Only positive integers
    
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

    def clean(self):
        super().clean()
        
        # Validate num_bedrooms
        if self.num_bedrooms < 0:
            raise ValidationError("Number of bedrooms cannot be negative.")
        
        # Validate num_bedrooms
        if self.available_bedrooms < 0:
            raise ValidationError("Number of available bedrooms cannot be negative.")
        
        # Validate num_bedrooms
        if self.num_bedrooms < self.available_bedrooms:
            raise ValidationError("Number of available bedrooms cannot be greater than number of bedrooms.")
        
        # Validate num_bathrooms
        if self.num_bathrooms < 0:
            raise ValidationError("Number of bathrooms cannot be negative.")
        
        # Validate monthly_rent
        if self.monthly_rent is None or self.monthly_rent <= 0:
            raise ValidationError("Monthly rent must be greater than zero.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean method is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class FoodEstablishment(Building):
    is_open_24_hours = models.BooleanField(default=False)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Establishment'
        verbose_name_plural = 'Establishments'

class BuildingPhoto(BaseModel):
    building = models.ForeignKey(Building, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='building_photos/')

    def __str__(self):
        return f'Photo for {self.building}'
    

class Review(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=20, null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    class Meta:
        # This ensures a user can only review a particular content (Rental/Food) once
        unique_together = ('user_profile', 'content_type', 'object_id')

    def __str__(self):
        return f'Review for {self.content_object} by {self.user_profile}'
    
    def analyze_sentiment(self):
        """
        Perform sentiment analysis on the comment field and update sentiment_label and sentiment_score.
        """
        if self.comment:
            # Using VADER
            analyzer = SentimentIntensityAnalyzer()
            sentiment = analyzer.polarity_scores(self.comment)
            self.sentiment_score = sentiment['compound']
            if sentiment['compound'] >= 0.05:
                self.sentiment_label = 'Positive'
            elif sentiment['compound'] <= -0.05:
                self.sentiment_label = 'Negative'
            else:
                self.sentiment_label = 'Neutral'

    def save(self, *args, **kwargs):
        # Perform sentiment analysis before saving
        self.analyze_sentiment()
        super().save(*args, **kwargs)

class RentalFavorite(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rental_favorites')
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'rental')  # Ensures a user can favorite a rental only once
    
    
    def __str__(self):
        return f'{self.user_profile} - {self.rental}'

class FoodEstablishmentFavorite(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='food_favorites')
    food_establishment = models.ForeignKey(FoodEstablishment, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'food_establishment')  # Ensures a user can favorite a food establishment only once
        
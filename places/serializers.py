from rest_framework import serializers
from .models import Rental, FoodEstablishment, Category, Review, BuildingPhoto, RentalFavorite
from django.contrib.contenttypes.models import ContentType
from user_profile.serializers import ProfileSerializer
from PIL import Image
import io
import base64

class BuildingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingPhoto
        fields = ['id', 'image']
    
    
    def get_image(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)  # Return full URL
        return None  # Return None if image doesn't exist or request is not available
        
class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'subcategories', 'created_at', 'updated_at']


    def get_subcategories(self, obj):
        # Access the subcategories of the current category
        if obj.subcategories.exists():
            return SubcategorySerializer(obj.subcategories.all(), many=True).data
        return []
    
class RentalSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()  
    user_profile = ProfileSerializer(read_only=True)
    photos = BuildingPhotoSerializer(many=True, read_only=True) 
    map_icon_bitmap = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    user_has_reviewed = serializers.SerializerMethodField()

    class Meta:
        model = Rental
        fields = '__all__'
    
    
    def get_user_has_reviewed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False

        # Check if the user has already reviewed this rental
        return Review.objects.filter(
            content_type=ContentType.objects.get_for_model(Rental),
            object_id=obj.id,
            user_profile=user.profile  # Assuming user has a related user profile
        ).exists()
    
    
    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            # If user is authenticated, check if they have favorited this rental
            return obj.favorited_by.filter(user_profile=request.user.profile).exists()
        return False  # If user is not authenticated, always return False
    
    def get_photos(self, obj):
        request = self.context.get('request')
        photo_urls = []

        for photo in obj.photos.all():  # Assuming photos is a related field
            if request:
                photo_url = request.build_absolute_uri(photo.image.url)  # Adjust `photo.image.url` based on your field
                photo_urls.append(photo_url)

        return photo_urls
    
    def get_map_icon_bitmap(self, obj):
        if obj.map_icon and obj.map_icon.path:
            try:
                image = Image.open(obj.map_icon.path)

                byte_arr = io.BytesIO()
                image.save(byte_arr, format='PNG')  # Save as PNG instead of BMP
                byte_arr = byte_arr.getvalue()

                bitmap = base64.b64encode(byte_arr).decode('utf-8')
                return bitmap
            except (FileNotFoundError, OSError) as e:
                return None
        return None

    def get_categories(self, obj):
        category_dict = {}

        all_categories = obj.categories.all()  

        for category in all_categories:
            if category.parent is None: 
                category_dict[category.id] = {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'subcategories': []  
                }
            else:  
                parent_id = category.parent.id
                
                if parent_id not in category_dict:
                    category_dict[parent_id] = {
                        'id': parent_id,
                        'name': category.parent.name,
                        'description': category.parent.description,
                        'subcategories': []
                    }

                category_dict[parent_id]['subcategories'].append({
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                })

        return list(category_dict.values()) 

    
class FoodEstablishmentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    user_profile = ProfileSerializer(read_only=True)
    photos = BuildingPhotoSerializer(many=True, read_only=True)  # Include photos
    map_icon_bitmap = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    user_has_reviewed = serializers.SerializerMethodField()


    class Meta:
        model = FoodEstablishment
        fields = '__all__'
    
    def get_user_has_reviewed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False

        # Check if the user has already reviewed this rental
        return Review.objects.filter(
            content_type=ContentType.objects.get_for_model(FoodEstablishment),
            object_id=obj.id,
            user_profile=user.profile  # Assuming user has a related user profile
        ).exists()
    
    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            # If user is authenticated, check if they have favorited this food establishment
            return obj.favorited_by.filter(user_profile=request.user.profile).exists()
        return False  # If user is not authenticated, always return False

    def get_map_icon_bitmap(self, obj):
        if obj.map_icon and obj.map_icon.path:
            try:
                image = Image.open(obj.map_icon.path)

                byte_arr = io.BytesIO()
                image.save(byte_arr, format='PNG')  # Save as PNG instead of BMP
                byte_arr = byte_arr.getvalue()

                bitmap = base64.b64encode(byte_arr).decode('utf-8')
                return bitmap
            except (FileNotFoundError, OSError) as e:
                return None
        return None

class ReviewSerializer(serializers.ModelSerializer):
    user_profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'content_type', 'object_id', 'stars', 'comment', 'user_profile']


class RentalFavoriteSerializer(serializers.ModelSerializer):
    rental = RentalSerializer() 

    class Meta:
        model = RentalFavorite
        fields = ['id', 'rental']
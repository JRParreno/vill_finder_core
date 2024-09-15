from rest_framework import serializers
from .models import BusinessCategory, BusinessSubCategory, BusinessPhotos, Business
from user_profile.serializers import ProfileSerializer

class BusinessPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPhotos
        fields = ['id', 'image']


class BusinessSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSubCategory
        fields = ['id', 'name']

class BusinessCategorySerializer(serializers.ModelSerializer):
    # Nested serializer to include subcategories
    category = BusinessSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = BusinessCategory
        fields = ['id', 'name', 'category']


class BusinessSerializer(serializers.ModelSerializer):
    category = BusinessSubCategorySerializer(many=True, read_only=True)
    business_photos = BusinessPhotosSerializer(many=True, read_only=True)
    user_profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = Business
        fields = '__all__'

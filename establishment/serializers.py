from rest_framework import serializers
from .models import BusinessCategory, BusinessSubCategory, BusinessPhotos, Business
from user_profile.serializers import ProfileSerializer
from PIL import Image
import io
import base64

class BusinessPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPhotos
        fields = ['id', 'image']


class BusinessSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSubCategory
        fields = ['id', 'name']

class BusinessCategorySerializer(serializers.ModelSerializer):
    category = BusinessSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = BusinessCategory
        fields = ['id', 'name', 'category',]

    


class BusinessSerializer(serializers.ModelSerializer):
    category = BusinessSubCategorySerializer(many=True, read_only=True)
    business_photos = BusinessPhotosSerializer(many=True, read_only=True)
    user_profile = ProfileSerializer(read_only=True)
    map_icon_bitmap = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = '__all__'

    def get_map_icon_bitmap(self, obj):
        if obj.map_icon:
            # Open the image file
            image = Image.open(obj.map_icon.path)

            # Convert the image to a byte stream (bitmap)
            byte_arr = io.BytesIO()
            image.save(byte_arr, format='PNG')  # Saving as BMP format
            byte_arr = byte_arr.getvalue()

            # Encode the byte array to base64 to send as JSON
            bitmap = base64.b64encode(byte_arr).decode('utf-8')
            return bitmap
        return None
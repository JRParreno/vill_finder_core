from rest_framework import serializers
from .models import Rental, FoodEstablishment, Category, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Add other fields as necessary


class RentalSerializer(serializers.ModelSerializer):
    categories = CategorySerializer()
    
    class Meta:
        model = Rental
        fields = '__all__'

class FoodEstablishmentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer()

    class Meta:
        model = FoodEstablishment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'content_type', 'object_id', 'stars', 'comment']
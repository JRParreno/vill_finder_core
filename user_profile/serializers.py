from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'first_name',
            'last_name',
            'username',
            'get_full_name'
        )
        extra_kwargs = {
            'username': {
                'read_only': True
            },
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'birthdate', 'contact_number', 'profile_photo']

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        request = self.context.get('request')
        # If profile_photo exists, build the absolute URI
        if instance.profile_photo:
            photo_url = request.build_absolute_uri(instance.profile_photo.url)
            representation['profile_photo'] = photo_url
        return representation

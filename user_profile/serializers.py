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

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(ProfileSerializer, self).__init__(*args, **kwargs)

    def get_profile_photo(self, data):
        request = self.context.get('request')
        if request and data.profile_photo:
            photo_url = data.profile_photo.url
            return request.build_absolute_uri(photo_url)
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Ensure request is not None
        if request and instance.profile_photo:
            # Build the absolute URL for the profile photo
            photo_url = request.build_absolute_uri(instance.profile_photo.url)
            representation['profile_photo'] = photo_url
        else:
            # Handle case where there is no photo or request
            representation['profile_photo'] = None  # or set to a default URL

        return representation


from django import utils
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.files.base import ContentFile
import base64


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



class ProfileSerializer(serializers.Serializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('__all__',)


    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(ProfileSerializer, self).__init__(*args, **kwargs)

    def get_profile_photo(self, data):
        request = self.context.get('request')
        photo_url = data.profile_photo.url
        return request.build_absolute_uri(photo_url)


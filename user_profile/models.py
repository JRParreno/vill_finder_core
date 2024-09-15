from django.db import models
from django.contrib.auth.models import User

from core.base_models import BaseModel

class UserProfile(BaseModel):
    class ProfileManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().select_related('user')

    
    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=25, null=True, blank=True)
    photo = models.CharField(max_length=255, null=True, blank=True)
    profile_photo = models.ImageField(
        upload_to='images/profiles/', blank=True, null=True)

    objects = ProfileManager()

    def __str__(self):
        return f'{self.user.last_name}- {self.user.first_name}'
from user_profile.models import UserProfile
from rest_framework import generics, permissions, response, status
from user_profile.models import UserProfile
from .serializers import ProfileSerializer


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profile_id = request.query_params.get('user_profile_id', None)

        if user_profile_id:
            # Fetch the profile using the provided user_profile_id and override the user
            try:
                user_profile = UserProfile.objects.get(pk=user_profile_id)
                user = user_profile.user  # Override user with the owner of the profile
            except UserProfile.DoesNotExist:
                return response.Response(
                    {"error_message": "Profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Default to using the current user's profile
            user_profiles = UserProfile.objects.filter(user=user)
            if user_profiles.exists():
                user_profile = user_profiles.first()
            else:
                return response.Response(
                    {"error_message": "Please setup your profile."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Prepare the response data
        data = {
            "pk": str(user.pk),
            "profilePk": str(user_profile.pk),
            "username": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "birthdate": str(user_profile.birthdate),
            "contactNumber": user_profile.contact_number,
            "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,
            "photo": user_profile.photo,
        }

        return response.Response(data, status=status.HTTP_200_OK)


import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model, AccessToken, RefreshToken, get_application_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.base import TokenView
from django.core.exceptions import ObjectDoesNotExist
from oauthlib.common import generate_token
from datetime import timedelta
from firebase_admin import auth
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.contrib.auth.models import User
from user_profile.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import time
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from places.models import FoodEstablishment, Rental, BuildingPhoto

# Your custom token verification function
def verify_firebase_token(id_token):
    try:
        # Directly verify the Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token  # Token is valid
    except auth.InvalidIdTokenError:
        raise ValueError("Invalid token")
    except auth.ExpiredIdTokenError:
        raise ValueError("Token expired")


class VerifyTokenView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access to this view

    @csrf_exempt
    def post(self, request):
        id_token = request.data.get('id_token', None)
        client_id = request.data.get('client_id', None)

        if id_token is None:
            return Response({"error": "Missing ID token"}, status=status.HTTP_400_BAD_REQUEST)
        if client_id is None:
            return Response({"error": "Missing client_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use the custom token verification function with leeway
            decoded_token = auth.verify_id_token(id_token)
            
            uid = decoded_token['uid']
            email = decoded_token.get('email', None)
            full_name = decoded_token.get('name', None)
            picture = decoded_token.get('picture', None)
            contact_number = decoded_token.get('phone_number', None)  # Profile picture URL
            
            name_parts = full_name.split(' ', 1)  # Split into two parts
            firstname = name_parts[0] if len(name_parts) > 0 else ''
            lastname = name_parts[1] if len(name_parts) > 1 else ''
            
            # Find or create the user based on UID
            user, created = User.objects.get_or_create(
                username=uid, defaults={'email': email, 'first_name': firstname, 'last_name': lastname}
            )
            if created:
                user.set_unusable_password()
                user.save()

            # Find or create the UserProfile
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'photo': picture,
                    'contact_number': contact_number
                }
            )
            
            if not profile_created:
                profile.photo = picture
                profile.contact_number = contact_number
                profile.save()

            # OAuth2: Generate access and refresh tokens
            application = get_application_model().objects.get(client_id=client_id)
            
            # Create access and refresh tokens
            access_token = AccessToken.objects.create(
                user=user,
                scope='read write',
                expires=timezone.now() + timedelta(hours=1),  # Set token expiry
                token=generate_token(),
                application=application
            )

            refresh_token = RefreshToken.objects.create(
                user=user,
                token=generate_token(),
                application=application,
                access_token=access_token
            )

            # Prepare response data
            data = {
                "message": "Token verified and user profile created/updated",
                "access_token": access_token.token,
                "refresh_token": refresh_token.token,
                "pk": str(user.pk),
                "profilePk": str(profile.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "contactNumber": profile.contact_number if profile.contact_number else None,
                "birthdate": str(profile.birthdate) if profile.birthdate else None,
                "photo": profile.photo,
                "profilePhoto": request.build_absolute_uri(profile.profile_photo.url) if profile.profile_photo else None,
            }

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class TokenViewWithUserId(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)

        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                try:
                    token = get_access_token_model().objects.get(
                        token=access_token)
                    
                    # Check if the user has a profile
                    profile = token.user.profile
                    if profile is None:
                        raise ObjectDoesNotExist("User profile does not exist")

                    app_authorized.send(
                        sender=self, request=request,
                        token=token)
                    
                    # Add user ID to the response body
                    data = {
                        "pk": str(token.user.pk),
                        "profilePk": str(profile.pk),
                        "username": token.user.username,
                        "firstName": token.user.first_name,
                        "lastName": token.user.last_name,
                        "email": token.user.email,
                        "contactNumber": profile.contact_number,
                        "birthdate": str(profile.birthdate),
                        "photo": profile.photo,
                        "profilePhoto": request.build_absolute_uri(profile.profile_photo.url) if profile.profile_photo else None,
                        "access_token": access_token,
                        "refresh_token": body.get("refresh_token")
                    }
                    
                    body = json.dumps(data)
                    
                except ObjectDoesNotExist:
                    # Handle case where user profile doesn't exist
                    return JsonResponse({'error_description': 'User profile does not exist'}, status=400)
   
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response
    


def registerShop(request):
    data = None
    if request.method == 'POST':
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        address = request.POST['address']
        contact_number = request.POST['contactNumber']
        email = request.POST['emailAddress']
        password = request.POST['password']

        if User.objects.filter(username=email).exists():
            data = {
                "error_message": "Email already exists"
            }


        if data is None:

            user = User.objects.create(
                username=email, email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.is_staff = True
            user.save()

            UserProfile.objects.create(user=user,
                                       contact_number=contact_number,
                                       )

            content_type_rental = ContentType.objects.get_for_model(Rental)
            content_type_food = ContentType.objects.get_for_model(FoodEstablishment)
            content_type_photos = ContentType.objects.get_for_model(
                BuildingPhoto)

            rental_permissions = Permission.objects.filter(
                content_type=content_type_rental)
            food_permissions = Permission.objects.filter(
                content_type=content_type_food)
            photos_permissions = Permission.objects.filter(
                content_type=content_type_photos)

            # To add permissions
            for perm in rental_permissions:
                user.user_permissions.add(perm)

            for perm in food_permissions:
                user.user_permissions.add(perm)
            
            for perm in photos_permissions:
                user.user_permissions.add(perm)

            return redirect('admin:index')

    return render(request, 'register.html', data)


def about_us(request):
    return render(request, 'about_us.html')
from rest_framework.views import APIView
from rest_framework import permissions, response, status, viewsets
from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django.contrib.contenttypes.models import ContentType

from core.paginate import ExtraSmallResultsSetPagination
from .models import Category, Rental, FoodEstablishment, Review, RentalFavorite, FoodEstablishmentFavorite
from .serializers import RentalSerializer, FoodEstablishmentSerializer, CategorySerializer, ReviewSerializer, RentalFavoriteSerializer
import math
from .utils import DistanceMixin

class CategoryListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
        
        # Get the 'q' query parameter from the request
        query = self.request.GET.get('q', None)
        
        # If a query parameter is provided, filter the queryset
        if query:
            queryset = queryset.filter(name__icontains=query)  # Use icontains for case-insensitive search

        return queryset

class PlaceSearchView(APIView, DistanceMixin):
    permission_classes = [permissions.AllowAny]
    pagination_class = ExtraSmallResultsSetPagination

    def get_parent_categories(self, category_id):
        """ Recursively get parent categories. """
        category = Category.objects.get(id=category_id)
        parent_categories = [category]
        while category.parent:
            category = category.parent
            parent_categories.append(category)
        return parent_categories

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        radius = 10000  # Radius in km
        category_id = request.GET.get('category_id')  # Get category ID from query params

        # Initialize rental and food results
        rental_results = Rental.objects.all()
        food_establishment_results = FoodEstablishment.objects.all()

        # Apply search filtering
        if query:
            rental_results = rental_results.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query)
            )
            food_establishment_results = food_establishment_results.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query)
            )

        # Filter by category if provided
        if category_id:
            try:
                # Get the category and its parent categories
                parent_categories = self.get_parent_categories(category_id)
                # Filter rentals and food establishments by category
                rental_results = rental_results.filter(categories__in=parent_categories)
                food_establishment_results = food_establishment_results.filter(categories__in=parent_categories)
            except Category.DoesNotExist:
                return response.Response({'error': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize lists for filtered results
        rental_within_radius = rental_results
        food_within_radius = []

        # If latitude and longitude are provided, filter by distance
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

            rental_within_radius = [
                rental for rental in rental_results
                if self.haversine(longitude, latitude, rental.longitude, rental.latitude) <= radius
            ]

            food_within_radius = [
                food for food in food_establishment_results
                if self.haversine(longitude, latitude, food.longitude, food.latitude) <= radius
            ]
        else:
            food_within_radius = food_establishment_results

        # Serialize the results for rentals and foods separately
        serialized_rentals = RentalSerializer(rental_within_radius, many=True, context={'request': request}).data
        serialized_foods = FoodEstablishmentSerializer(food_within_radius, many=True, context={'request': request}).data


        # Paginate rentals and foods separately
        paginator = self.pagination_class()
        paginated_rentals = paginator.paginate_queryset(serialized_rentals, request)
        paginated_foods = paginator.paginate_queryset(serialized_foods, request)

        # Combine the results into a structured response
        results = {
            'rentals': paginated_rentals,
            'foods': paginated_foods
        }

        return paginator.get_paginated_response(results)

class BaseSearchView(ListAPIView, DistanceMixin):
    permission_classes = [permissions.AllowAny]
    query_param = 'q'
    category_param = 'category_id'
    latitude_param = 'latitude'
    longitude_param = 'longitude'
    radius_param = 'radius'
    is_featured = 'is_featured'

    def get_parent_categories(self, category_id):
        """ Recursively get parent categories. """
        category = self.get_category_model().objects.get(id=category_id)
        parent_categories = [category]
        while category.parent:
            category = category.parent
            parent_categories.append(category)
        return parent_categories

    def filter_queryset(self, queryset):
        query = self.request.GET.get(self.query_param, '')
        category_id = self.request.GET.get(self.category_param)
        latitude = self.request.GET.get(self.latitude_param)
        longitude = self.request.GET.get(self.longitude_param)
        radius = self.request.GET.get(self.radius_param, 10)
        is_featured  = self.request.GET.get('is_featured', 'false').lower() == 'true'
        
        if is_featured:
            queryset =  queryset.filter(is_featured=True)
        
        # Apply search filtering
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query)
            )

        # Filter by category if provided
        if category_id:
            try:
                parent_categories = self.get_parent_categories(category_id)
                queryset = queryset.filter(categories__in=parent_categories)
            except self.get_category_model().DoesNotExist:
                return response.Response({'error': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by distance if latitude and longitude are provided
        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                radius = float(radius)

                # Filter queryset by calculating the distance between user location and object location
                queryset = [
                    obj for obj in queryset
                    if self.haversine(longitude, latitude, obj.longitude, obj.latitude) <= radius
                ]
            except ValueError:
                return response.Response({'error': 'Invalid coordinates'}, status=status.HTTP_400_BAD_REQUEST)

        return queryset

    def get_queryset(self):
        return self.filter_queryset(self.queryset)

    def get_category_model(self):
        raise NotImplementedError("You should implement get_category_model in the subclass.")

    def get_serializer_class(self):
        raise NotImplementedError("You should implement get_serializer_class in the subclass.")


# Define specific views for Rental and FoodEstablishment
class RentalSearchView(BaseSearchView):
    queryset = Rental.objects.all()

    def get_category_model(self):
        return Category

    def get_serializer_class(self):
        return RentalSerializer


class FoodEstablishmentSearchView(BaseSearchView):
    queryset = FoodEstablishment.objects.all()

    def get_category_model(self):
        return Category

    def get_serializer_class(self):
        return FoodEstablishmentSerializer
    


class BaseRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'  # Assuming you're looking up by the 'id' field, adjust if necessary
    
    def get_queryset(self):
        return self.queryset

    def get_category_model(self):
        raise NotImplementedError("You should implement get_category_model in the subclass.")

    def get_serializer_class(self):
        raise NotImplementedError("You should implement get_serializer_class in the subclass.")

class RentalRetrieveUpdateView(BaseRetrieveUpdateView):
    queryset = Rental.objects.all()

    def get_category_model(self):
        return Category

    
    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return response.Response({"error_message": "User must be authenticated to add/remove favorites."}, status=status.HTTP_401_UNAUTHORIZED)

        rental = self.get_object()
        user_profile = request.user.profile

        # Check if 'favorite' is passed in the request data
        favorite = request.data.get('favorite')
        if favorite is not None:
            if favorite:  # Add to favorites
                RentalFavorite.objects.get_or_create(user_profile=user_profile, rental=rental)
            else:  # Remove from favorites
                RentalFavorite.objects.filter(user_profile=user_profile, rental=rental).delete()

        return super().patch(request, *args, **kwargs)

    def get_serializer_class(self):
        return RentalSerializer  # Return the serializer class for Rental

class FoodEstablishmentRetrieveUpdateView(BaseRetrieveUpdateView):
    queryset = FoodEstablishment.objects.all()
    serializer_class = FoodEstablishmentSerializer

    def get_category_model(self):
        return Category

    
    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return response.Response({"error_message": "User must be authenticated to add/remove favorites."}, status=status.HTTP_401_UNAUTHORIZED)

        food_establishment = self.get_object()
        user_profile = request.user.profile

        # Check if 'favorite' is passed in the request data
        favorite = request.data.get('favorite')
        if favorite is not None:
            if favorite:  # Add to favorites
                FoodEstablishmentFavorite.objects.get_or_create(user_profile=user_profile, food_establishment=food_establishment)
            else:  # Remove from favorites
                FoodEstablishmentFavorite.objects.filter(user_profile=user_profile, food_establishment=food_establishment).delete()

        return super().patch(request, *args, **kwargs)

    def get_serializer_class(self):
        return FoodEstablishmentSerializer 
    
class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = ExtraSmallResultsSetPagination

    def list(self, request, *args, **kwargs):
        # Get parameters from the request
        content_type_param = self.request.query_params.get('content_type', None)
        object_id_param = self.request.query_params.get('object_id', None)

        queryset = super().get_queryset()

        # Filter by content_type (e.g., 'rental' or 'foodestablishment')
        if content_type_param:
            try:
                content_type = ContentType.objects.get(model=content_type_param)
                queryset = queryset.filter(content_type=content_type)
            except ContentType.DoesNotExist:
                return queryset.none()  # Return empty queryset if content_type is invalid

        # Filter by object_id
        if object_id_param:
            queryset = queryset.filter(object_id=object_id_param)

        # Get paginated results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        content_type_str = request.data.get('content_type')
        object_id = request.data.get('object_id')
        stars = request.data.get('stars')
        comment = request.data.get('comment')

        # Ensure content_type is either 'rental' or 'foodestablishment'
        if content_type_str not in ['rental', 'foodestablishment']:
            return response.Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the content type model (Rental or FoodEstablishment)
        content_type = ContentType.objects.get(model=content_type_str)

        # Check if a review already exists by this user for the given object
        review, created = Review.objects.update_or_create(
            content_type=content_type,
            object_id=object_id,
            user_profile=user.profile,
            defaults={'stars': stars, 'comment': comment}
        )

        serializer = self.get_serializer(review)

        if created:
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)  # New review created
        else:
            return response.Response(serializer.data, status=status.HTTP_200_OK)  # Existing review updated

    def update(self, request, *args, **kwargs):
        """ Update an existing review """
        instance = self.get_object()

        # Ensure that only the user who created the review can update it
        if instance.user_profile != request.user.profile:
            return Response({'error': 'You are not allowed to update this review.'}, status=status.HTTP_403_FORBIDDEN)

        # Handle partial updates or full updates
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        # Validate data
        if 'stars' in request.data:
            stars = request.data['stars']
            if stars is not None and (stars < 1 or stars > 5):
                return response.Response({'error': 'Stars must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        review.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        """ Save the updated review """
        serializer.save()
        

class RentalFavoriteListView(ListAPIView):
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        # Get the current user's profile
        user_profile = self.request.user.profile

        # Retrieve Rental objects that are favorited by the user
        return Rental.objects.filter(favorited_by__user_profile=user_profile)

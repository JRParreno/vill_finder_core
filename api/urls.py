from django.urls import path, include
from user_profile.views import ProfileView
from places.views import (PlaceSearchView, FoodEstablishmentSearchView, 
     RentalSearchView, CategoryListView, ReviewViewSet, RentalRetrieveUpdateView, FoodEstablishmentRetrieveUpdateView)
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
     path('profile', ProfileView.as_view(), name='profile'),

     path('categories/', CategoryListView.as_view(), name='category-list'),

     path('places/search/', PlaceSearchView.as_view(), name='places'),
     path('places/rental/', RentalSearchView.as_view(), name='rental-search'),
     path('places/rental/detail/<int:id>/', RentalRetrieveUpdateView.as_view(), name='rental-detail'),

     path('places/food/', FoodEstablishmentSearchView.as_view(), name='food-search'),
     path('places/food/detail/<int:id>/', FoodEstablishmentRetrieveUpdateView.as_view(), name='food-establishment-detail'),

     path('', include(router.urls)),
]

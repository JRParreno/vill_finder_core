from django.urls import path
from user_profile.views import ProfileView
from establishment.views import BusinessCategoryListView, BusinessListView

app_name = 'api'

urlpatterns = [
     path('profile', ProfileView.as_view(), name='profile'),

     path('business-categories/', BusinessCategoryListView.as_view(), name='business-category-list'),
     path('businesses/', BusinessListView.as_view(), name='business-list'),
]

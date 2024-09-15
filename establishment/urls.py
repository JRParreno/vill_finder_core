# urls.py

from django.urls import path
from .views import fetch_subcategories

urlpatterns = [
    path('admin/api/subcategories/', fetch_subcategories, name='fetch_subcategories'),
]

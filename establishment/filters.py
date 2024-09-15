from django_filters import rest_framework as filters
from .models import Business

class BusinessFilter(filters.FilterSet):
    category_id = filters.NumberFilter(field_name='category__id')  # Filter by category ID
    business_name = filters.CharFilter(field_name='name', lookup_expr='icontains')  # Filter by business name

    class Meta:
        model = Business
        fields = ['category_id', 'business_name']  # Expose the fields you want to filter

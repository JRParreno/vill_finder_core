from django_filters import rest_framework as filters
from .models import Business

class BusinessFilter(filters.FilterSet):
    category_id = filters.NumberFilter(field_name='category__categories__id')  # Traversing from Business -> BusinessSubCategory -> BusinessCategory
    business_name = filters.CharFilter(field_name='name', lookup_expr='icontains')  # Filter by business name

    # Add filters for map bounds
    min_latitude = filters.NumberFilter(field_name='latitude', lookup_expr='gte')
    max_latitude = filters.NumberFilter(field_name='latitude', lookup_expr='lte')
    min_longitude = filters.NumberFilter(field_name='longitude', lookup_expr='gte')
    max_longitude = filters.NumberFilter(field_name='longitude', lookup_expr='lte')


    class Meta:
        model = Business
        fields = ['category_id', 'business_name', 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude']

from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import BusinessCategory, Business
from .serializers import BusinessCategorySerializer, BusinessSerializer
from .filters import BusinessFilter

class BusinessCategoryListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = BusinessCategory.objects.all()
    serializer_class = BusinessCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__name']


class BusinessListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BusinessFilter

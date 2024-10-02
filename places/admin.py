from django.contrib import admin
from .models import Category, Rental, FoodEstablishment, BuildingPhoto
from django_admin_geomap import ModelAdmin

class BuildingPhotoInline(admin.TabularInline):
    model = BuildingPhoto
    extra = 1  # Number of empty forms to display
    max_num = 10  # Maximum number of photos allowed

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'parent')
    search_fields = ('name', 'description')

@admin.register(Rental)
class RentalAdmin(ModelAdmin):
    list_display = ('name', 'user_profile', 'address', 'num_bedrooms', 'num_bathrooms',)
    search_fields = ('name', 'address', 'user_profile__username')
    list_filter = ('user_profile',)
    inlines = [BuildingPhotoInline]  # Inline for building photos

    # Geomap settings
    geomap_show_map_on_list = False
    geomap_default_zoom = "15"
    geomap_item_zoom = "15"
    geomap_autozoom = "15"
    geomap_default_longitude = "121.0164655"
    geomap_default_latitude = "14.5231427"
    geomap_field_longitude = "id_longitude"
    geomap_field_latitude = "id_latitude"
    geomap_height = "700px"
    
    class Media:
        js = ('js/hide_map.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove is_food_establishment from the form
        if 'is_food_establishment' in form.base_fields:
            del form.base_fields['is_food_establishment']
        return form

@admin.register(FoodEstablishment)
class FoodEstablishmentAdmin(ModelAdmin):
    list_display = ('name', 'user_profile', 'address', 'opening_time', 'closing_time')
    search_fields = ('name', 'address', 'user_profile__username')
    list_filter = ('user_profile',)
    inlines = [BuildingPhotoInline]  # Inline for building photos

    # Geomap settings
    geomap_show_map_on_list = False
    geomap_default_zoom = "15"
    geomap_item_zoom = "15"
    geomap_autozoom = "15"
    geomap_default_longitude = "121.0164655"
    geomap_default_latitude = "14.5231427"
    geomap_field_longitude = "id_longitude"
    geomap_field_latitude = "id_latitude"
    geomap_height = "700px"

    class Media:
        js = ('js/hide_map.js',)

    def save_model(self, request, obj, form, change):
        if not change:  # This means it's a new object
            obj.is_food_establishment = True  # Automatically set to True
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Remove is_food_establishment from the form
        if 'is_food_establishment' in form.base_fields:
            del form.base_fields['is_food_establishment']
        return form
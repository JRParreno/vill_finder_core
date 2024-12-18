from django.contrib import admin
from .models import Category, Rental, FoodEstablishment, BuildingPhoto, Review, RentalFavorite
from django_admin_geomap import ModelAdmin
from django.contrib.contenttypes.models import ContentType


admin.site.register(RentalFavorite)
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
    list_filter = ('is_featured',)
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
        
        # Remove 'is_food_establishment' field if it exists
        if 'is_food_establishment' in form.base_fields:
            del form.base_fields['is_food_establishment']
        
        # Remove 'user_profile' if the user is staff (but not superuser)
        if request.user.is_staff and not request.user.is_superuser:
            if 'user_profile' in form.base_fields:
                del form.base_fields['user_profile']
        
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Restrict queryset for staff users to only show their associated rentals
        if not request.user.is_superuser:
            return qs.filter(user_profile__user=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        # Automatically assign the current user's profile as user_profile if the user is staff
        if not request.user.is_superuser and not change:
            obj.user_profile = request.user.profile
        super().save_model(request, obj, form, change)

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
        # Automatically set `is_food_establishment` to True for new objects
        if not change:
            obj.is_food_establishment = True
            # Set the user_profile to the logged-in user's profile for staff users
            if not request.user.is_superuser:
                obj.user_profile = request.user.profile
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Remove `is_food_establishment` from the form fields
        if 'is_food_establishment' in form.base_fields:
            del form.base_fields['is_food_establishment']
        
        # Remove `user_profile` if the user is staff (but not superuser)
        if request.user.is_staff and not request.user.is_superuser:
            if 'user_profile' in form.base_fields:
                del form.base_fields['user_profile']
        
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Restrict queryset for staff users to only show their associated food establishments
        if not request.user.is_superuser:
            return qs.filter(user_profile__user=request.user)
        return qs



class ReviewContentTypeFilter(admin.SimpleListFilter):
    title = 'Content Type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        # Only include FoodEstablishment and Rental in the filter options
        return (
            (ContentType.objects.get_for_model(FoodEstablishment).id, 'Food Establishment'),
            (ContentType.objects.get_for_model(Rental).id, 'Rental'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type__id=self.value())
        return queryset

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('content_object_display', 'comment', 'created_at')  # Assuming you have a `created_at` field in the model
    search_fields = ('comment',)
    list_filter = (ReviewContentTypeFilter,)
    
    def get_queryset(self, request):
        # Optimize queries if you need to display related fields
        qs = super().get_queryset(request)
        return qs.select_related('content_type')

    def content_object_display(self, obj):
        """Custom method to display the object being reviewed."""
        return str(obj.content_object)
    content_object_display.short_description = 'Reviewed Item'  # Optional: set a column header for the custom method

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit the content type to FoodEstablishment and Rental
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(model__in=['foodestablishment', 'rental'])  # Use the correct lowercase model names
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct
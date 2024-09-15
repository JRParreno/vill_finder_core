from django.contrib import admin
from .models import Business, BusinessCategory, BusinessSubCategory, BusinessPhotos
from django_admin_geomap import ModelAdmin


class BusinessPhotoTabularInLine(admin.TabularInline):
    model = BusinessPhotos
    fields = ('business', 'image')


class BusinessSubCategoryInline(admin.TabularInline):
    model = BusinessSubCategory
    extra = 1  # Number of empty forms to display

@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    inlines = [BusinessSubCategoryInline]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(BusinessSubCategory)
class BusinessSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('categories',) 

@admin.register(Business)
class BusinessAdmin(ModelAdmin):
    geomap_show_map_on_list = False
    geomap_default_zoom = "15"
    geomap_item_zoom = "15"
    geomap_autozoom = "15"
    geomap_item_zoom = "15"
    geomap_default_longitude = "121.0164655"
    geomap_default_latitude = "14.5231427"
    geomap_field_longitude = "id_longitude"
    geomap_field_latitude = "id_latitude"
    geomap_height = "700px"
    list_display = ('name', 'user_profile', 'open_time', 'close_time', 'updated_at', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('category',) 
    filter_horizontal = ('category',) 
    inlines = [BusinessPhotoTabularInLine,]
    
    
    class Media:
        js = ('js/hide_map.js',)

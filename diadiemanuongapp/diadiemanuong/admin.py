from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .dao import count_restaurant_by_cat
from .models import Category, Restaurant, User, Tag, Dish


# Register your models here.
class RestaurantAppAdminSite(admin.AdminSite):
    site_header = "HỆ THỐNG ĐỊA ĐIỂM ĂN UỐNG"

    def get_urls(self):
        return [
            path('diadiemanuong-stats/', self.stats_view)
        ] + super().get_urls()

    def stats_view(self, request):
        stats = count_restaurant_by_cat()
        return TemplateResponse(request, 'admin/stats.html', context={
            'stats': stats
        })


admin_site = RestaurantAppAdminSite(name="myapp")


class RestaurantTagInlineAdmin(admin.TabularInline):
    model = Restaurant.tags.through


class DishTagInlineAdmin(admin.TabularInline):
    model = Dish.tags.through


# tao form de upload anh bang CKEditor
class RestaurantForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'image', 'description', 'category', 'tags']


class DishForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'image', 'tags']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_filter = ['id', 'name']


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'user', 'is_approved', 'active']
    search_fields = ['name', 'is_approved', 'active']
    actions = ['approve_restaurants']
    list_filter = ['id', 'name']
    form = RestaurantForm
    inlines = [RestaurantTagInlineAdmin]
    readonly_fields = ['ava']

    class Media:
        css = {
            'all': ('/static/css/style.css',)
        }

    def ava(self, obj):
        if obj:
            return mark_safe(
                '<img src="/static/{url}" width="120" />' \
                    .format(url=obj.image.name)
            )

    def approve_restaurants(self, request, queryset):
        queryset.update(is_approved=True)
        queryset.update(active=True)

    approve_restaurants.short_description = "Approve selected restaurants"


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class DishAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'description']
    form = DishForm
    inlines = [DishTagInlineAdmin]
    readonly_fields = ['ava']

    def ava(self, obj):
        if obj:
            return mark_safe(
                '<img src="/static/{url}" width="120" />' \
                    .format(url=obj.image.name)
            )


# Register model here.
admin_site.register(Category, CategoryAdmin)
admin_site.register(Restaurant, RestaurantAdmin)
admin_site.register(User)
admin_site.register(Tag, TagAdmin)
admin_site.register(Dish)
# admin_site.register(Login)

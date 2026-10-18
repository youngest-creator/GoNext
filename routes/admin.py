from django.contrib import admin
from .models import Route, Review

admin.site.site_header = "Панель управления GoNext (Разработчик: Максим Фирсов)"
admin.site.site_title = "GoNext Админ"
admin.site.index_title = "Управление базой данных"


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('title', 'country_and_points', 'days', 'distance_km', 'budget', 'currency', 'transport', 'author', 'created_at')
    search_fields = ('title', 'country_and_points', 'description')
    list_filter = ('currency', 'transport', 'days', 'author')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('route', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('text', 'route__title', 'author__username')
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from routes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('route/<int:route_id>/', views.route_detail, name='route_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('edit/<int:route_id>/', views.edit_route, name='edit_route'),
    path('delete/<int:route_id>/', views.delete_route, name='delete_route'),
    path('favorite/<int:route_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('print/<int:route_id>/', views.print_route, name='print_route'),
    path('review/<int:route_id>/', views.add_review, name='add_review'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='routes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
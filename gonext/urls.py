from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from routes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('delete/<int:route_id>/', views.delete_route, name='delete_route'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='routes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
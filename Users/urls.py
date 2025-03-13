from django.urls import path
from . import views

# Define URL patterns for the Users app
urlpatterns = [
    # Route for the welcome/home page
    path('', views.home, name='welcome'),
    # Route for user login page
    path('login/', views.login_view, name='login'),
    # Route for user registration page
    path('signup/', views.signup_view, name='signup'),
    # Route for admin/manager login page
    path('admin_login/', views.admin_login, name='admin_login'),
]
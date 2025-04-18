from django.urls import path
from . import views

# Define URL patterns for the Users app
urlpatterns = [
    # Route for the welcome/home page
    path('', views.home, name='home'),
    # Route for user login page
    path('login/', views.login_view, name='login'),
    # Route for user registration page
    path('signup/', views.signup_view, name='signup'),
    # Route for admin/manager login page
    # path('django-admin/', views.admin_login, name='django-admin'),
   
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('reset-password/<str:uidb64>/<str:token>/', views.resetPassword, name='resetPassword'),
    path('password-reset-confirm/', views.passwordResetConfirm, name='passwordResetConfirm'),
    path ('engineer_dashboard/', views.engineer_dashboard, name='engineer_dashboard'),
    path('logout/', views.logout_view, name='logout')
    ]
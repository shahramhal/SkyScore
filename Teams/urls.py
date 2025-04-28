from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app
    path('senmanager/', views.getsenman_overview, name='SenManagerDash'),
     # Add your Teams app URLs here if needed
    # path('', include('Teams.urls')),

]

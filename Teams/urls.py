from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app
    path('senmanager/', views.department_dashboard, name='sen_manager'),
     # Add your Teams app URLs here if needed
    # path('', include('Teams.urls')),

    path('get_departments/', views.get_departments, name='get_departments'),
    path('get_department_data/', views.get_department_data, name='get_department_data')
]

from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app
    path('senmanager/', views.getsenman_overview, name='SenManagerDash'),
    path('department-summary/',views.department_summary, name='department_summary'),
    path('api/department-data/', views.department_data, name='department_data'),
    path('senmanagerprog/', views.getsenmanprogress, name='SenManp2'),
    # path('', include('Teams.urls')),

]

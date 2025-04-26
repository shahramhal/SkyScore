from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app
    path('senmanager/', views.getsenman_overview, name='SenManagerDash'),
     # Add your Teams app URLs here if needed
    # path('', include('Teams.urls')),

<<<<<<< HEAD
   
=======
    path('get_departments/', views.get_departments, name='get_departments'),
    path('get_department_data/', views.get_department_data, name='get_department_data'),
    path ('get_settings/', views.get_settings, name='get_settings')
>>>>>>> 7db597e2870cd9def8c2a55240fc87424d3bfc6a
]

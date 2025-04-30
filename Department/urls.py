from django.urls import path
from . import views

urlpatterns = [
    path('departmentDashboard/', views.departmentDashboard, name='dept_lead_dashboard'),
    path('department/settings/', views.department_settings, name='department_settings'),
    path('get_data/', views.get_data, name='get_data'),
    path('view_summary/<int:team_id>/', views.view_summary, name='view_summary'),
]

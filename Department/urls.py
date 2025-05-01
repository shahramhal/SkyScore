from django.urls import path
from . import views

urlpatterns = [
    path('departmentDashboard/', views.departmentDashboard, name='departmentDashboard'),
    path('department/settings/', views.department_settings, name='department_settings'),
    path('get_data/', views.get_data, name='get_data'),
    path('view_summary/<int:team_id>/', views.view_summary, name='view_summary'),
    path('reports/', views.department_reports, name='department_reports'),
]

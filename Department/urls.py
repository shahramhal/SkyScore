# department/urls.py

from django.urls import path
from . import views



urlpatterns = [

    path('departmentDashboard/', views.departmentDashboard, name='dept_lead_dashboard'),
    path('view_summary/<int:team_id>/', views.view_summary, name='view_summary'),
    path('deptreports/', views.department_reports, name='department_reports'),
    path('departmentSettings/', views.department_settings, name='department_settings'),
    path('reports/', views.department_reports, name='dept_reports'),
    path('healthcheck/', views.health_check_view, name='health_check_placeholder'), 


    # 1) Department Leader landing page (pick your team)
    path('dashboard/', views.department_dashboard, name='dashboard'),
    path('reports/', views.department_reports, name='reports'),

]

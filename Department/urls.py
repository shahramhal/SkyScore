from django.urls import path
from . import views

urlpatterns = [
    path('departmentDashboard/', views.departmentDashboard, name='dept_lead_dashboard'),
    path('view_summary/<int:team_id>/', views.view_summary, name='view_summary'),
    path('reports/', views.department_reports, name='department_reports'),
]

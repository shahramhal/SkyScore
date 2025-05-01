# department/urls.py

from django.urls import path
from . import views

app_name = 'department'

urlpatterns = [
    # 1) Department Leader landing page (pick your team)
    path('dashboard/', views.department_dashboard, name='dashboard'),
    path('reports/', views.department_reports, name='reports'),
]

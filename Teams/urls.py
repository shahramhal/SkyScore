from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app
    path('senmanager/', views.getsenman_overview, name='SenManagerDash'),
    path('getsenmanagerprog/', views.getsenmanprogress, name='SenManagerprog'),
    path('department-summary/',views.department_summary, name='department_summary'),
    path('api/department-data/', views.department_data, name='department_data'),
    path('teamleaddash/', views.team_lead_dashboard, name='teamleaddash'),
    path('teamleadprog/', views.team_progress, name='teamleadprog'),
    path('api/engineering-metrics/', views.engineering_metrics, name='engineering_metrics'),
    path('settings_sm/',views.get_settings_SM, name = 'settings_sm'),
    path('debug_cards/', views.debug_cards, name='debug_cards'),
    
    
    
    # path('', include('Teams.urls')),

]

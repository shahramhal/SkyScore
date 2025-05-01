from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app
    path('senmanager/', views.getsenman_overview, name='SenManagerDash'),
    path('getsenmanagerprog/', views.getsenmanprogress, name='SenManagerprog'),
    path('profile/', views.senman_profile, name='senman_profile'),
    path('profile/update/', views.update_profile, name='senman_update_profile'),
    path('profile/change-password/', views.change_password, name='senman_change_password'),
    
    path('department-summary/',views.department_summary, name='department_summary'),
    path('api/department-data/', views.department_data, name='department_data'),
    path('teamleaddash/', views.team_lead_dashboard, name='teamleaddash'),
    path('teamleadprog/', views.team_progress, name='teamleadprog'),
    path('voting_dashboard/', views.team_lead_voting, name='team_voting_dashboard'),
    path ('team_lead_profile/', views.team_lead_profile, name='team_lead_profile'),
    path('update_profile/', views.team_update_profile, name='update_profile'),
    path('voting-card/<int:card_id>/', views.team_lead_vote_card, name='team_vote_card'),
    path('submit-vote/<int:card_id>/', views.team_lead_submit_vote, name='team_submit_vote'),
    path('api/engineering-metrics/', views.engineering_metrics, name='engineering_metrics'),
    path('settings_sm/',views.get_settings_SM, name = 'settings_sm'),
    path('settings_tl/',views.get_settings_TL, name = 'settings_tl'),
    
    
    
    # path('', include('Teams.urls')),

]

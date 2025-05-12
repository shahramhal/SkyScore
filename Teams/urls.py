# Author: Hamza Hassan (W2044381)
# File: Teams/urls.py
# Purpose: Route HTTP endpoints to the Senior Manager, Team Lead and Department Lead views.
# Date:    20 April 2025
# Last updated: 30 April 2025 (added senior-metrics API and settings routes)

from django.urls import path, include
from . import views

urlpatterns = [
    # Include URLs from the Users app

    # Senior Manager Dashboard
    path('senmanager/', views.getsenman_overview, name='SenManagerDash'),
    # Back in March I realized my prog view needed to handle missing dept IDs
    path('getsenmanagerprog/', views.getsenmanprogress, name='SenManagerprog'),

    # Senior Manager Profile
    path('profile/', views.senman_profile, name='senman_profile'),
    path('profile/update/', views.update_profile, name='senman_update_profile'),
    path('profile/change-password/', views.change_password, name='senman_change_password'),
    
    # Department Summary & Data API
    path('department-summary/',views.department_summary, name='department_summary'),

    # I originally forgot to namespace this under /api/, fixed on feature/api_cleanup
    path('api/department-data/', views.department_data, name='department_data'),

    # Team Lead Dashboard & Voting
    path('teamleaddash/', views.team_lead_dashboard, name='teamleaddash'),

    # Shows progress charts for a single team
    path('teamleadprog/', views.team_progress, name='teamleadprog'),
    path('voting_dashboard/', views.team_lead_voting, name='team_voting_dashboard'),
    path ('team_lead_profile/', views.team_lead_profile, name='team_lead_profile'),
    path('update_profile/', views.team_update_profile, name='update_profile'),
    # Navigates between individual card voting pages
    path('voting-card/<int:card_id>/', views.team_lead_vote_card, name='team_vote_card'),
    path('submit-vote/<int:card_id>/', views.team_lead_submit_vote, name='team_submit_vote'),

    # Engineering Metrics API
    # Provides JSON for the Engineering Ops department charts
    path('api/engineering-metrics/', views.engineering_metrics, name='engineering_metrics'),

    # Settings Pages
    path('settings_sm/',views.get_settings_SM, name = 'settings_sm'),
    path('settings_tl/',views.get_settings_TL, name = 'settings_tl'),
    
    
    
    # path('', include('Teams.urls')),

]

from django.urls import path
from . import views

urlpatterns = [
    path('voting/dashboard/', views.votingDashboard, name='votingDashboard'),
    path('voting/card/<int:card_id>/', views.vote_card, name='vote_card'),
    path('voting/submit/<int:card_id>/', views.submit_vote, name='submit_vote'),
    path('voting/session/<int:session_id>/', views.view_session, name='view_session'),
    path('voting/start-new-session/', views.start_new_session, name='start_new_session'),
]

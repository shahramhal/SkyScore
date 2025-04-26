from django.urls import path
from . import views

urlpatterns = [
    path('votingDashboard/', views.votingDashboard, name='votingDashboard'),
    path('vote_card/<int:card_id>/', views.vote_card, name='vote_card'),
    path('submit_vote/<int:card_id>/', views.submit_vote, name='submit_vote'),
]

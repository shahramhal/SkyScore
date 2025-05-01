from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from Teams.models import Team
from Users.models import User, Healthcheckcard, Vote, Department
from datetime import datetime, timedelta
from django.db.models import Avg
import json
from django.urls import reverse
from django.urls import reverse_lazy
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib import messages

def departmentDashboard(request):
    teams = Team.objects.all()
    return render(request, 'DeptLeadpg2.html', {'teams': teams})

def department_settings(request):
    return render(request, 'DeptLeadSetting.html')

def get_data(request):
    view_type = request.GET.get('view')
    if view_type == 'teams':
        data = list(Team.objects.values('teamid', 'teamname'))
    else:
        data = []
    return JsonResponse(data, safe=False)

def view_summary(request, team_id):
    team = get_object_or_404(Team, teamid=team_id)
    teams = Team.objects.all()
    return render(request, 'DeptLeadVT.html', {
        'current_team': team,
        'teams': teams
    })

def department_reports(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        # Get the user and their department
        user = User.objects.get(userID=request.session['user_id'])
        if not user.departmentid:
            return redirect('departmentDashboard')
            
        # Get teams in the department
        teams = Team.objects.filter(departmentid=user.departmentid)
        
        # Get all health check cards
        health_cards = Healthcheckcard.objects.all()
        
        # Get recent votes for visualization (last month)
        today = datetime.now().date()
        one_month_ago = today - timedelta(days=30)
        
        # Get all users in the department's teams
        department_users = User.objects.filter(teamid__in=teams)
        
        # Get votes for the department in the last month
        votes = Vote.objects.filter(
            userid__in=department_users,
            votingdate__gte=one_month_ago
        )
        
        # Calculate metrics for each team
        team_metrics = []
        for team in teams:
            team_users = User.objects.filter(teamid=team)
            team_votes = votes.filter(userid__in=team_users)
            
            # Calculate average scores for each category
            teamwork_score = team_votes.filter(cardid__cardname='Teamwork').aggregate(avg=Avg('votevalue'))['avg'] or 0
            mission_score = team_votes.filter(cardid__cardname='Mission').aggregate(avg=Avg('votevalue'))['avg'] or 0
            speed_score = team_votes.filter(cardid__cardname='Speed').aggregate(avg=Avg('votevalue'))['avg'] or 0
            value_score = team_votes.filter(cardid__cardname='Delivering value').aggregate(avg=Avg('votevalue'))['avg'] or 0
            
            team_metrics.append({
                'team_name': team.teamname,
                'health_score': round(teamwork_score, 2),
                'mission_score': round(mission_score, 2),
                'speed_score': round(speed_score, 2),
                'value_score': round(value_score, 2),
                'total_votes': team_votes.count(),
                'member_count': team_users.count()
            })
        
        context = {
            'department_name': user.departmentid.departmentname,
            'teams': teams,
            'team_metrics': json.dumps(team_metrics),
            'total_teams': len(teams),
            'total_members': department_users.count(),
            'total_votes': votes.count(),
            'active_page': 'reports'
        }
        
        return render(request, 'department_reports.html', context)
        
    except User.DoesNotExist:
        return redirect('login')
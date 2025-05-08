
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from Teams.models import Team
from Users.models import User, Healthcheckcard, Vote, Department
from datetime import datetime, timedelta, date
from django.db.models import Avg
import json
from django.urls import reverse
from django.urls import reverse_lazy
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib import messages


from django.http import JsonResponse, HttpResponse
from Teams.models import Team, User, Healthcheckcard, Vote, Department, Summary
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, timedelta

def departmentDashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(userID=request.session['user_id'])

        if hasattr(user, 'departmentid') and user.departmentid is not None:
            teams = Team.objects.filter(departmentid=user.departmentid)
        else:
            teams = []

        return render(request, 'DeptLeadpg2.html', {'teams': teams})

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')


def department_settings(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'DeptLeadSetting.html')


def health_check_view(request):
    if 'user_id' not in request.session or 'selected_team_id' not in request.session:
        return redirect('login')

    try:
        team_id = request.session['selected_team_id']
        team = Team.objects.get(teamid=team_id)

        return render(request, 'DeptLeadHealthCheck.html', {'team': team})

    except Team.DoesNotExist:
        return render(request, 'DeptError.html', {'message': 'Selected team not found. Please go back and select again.'})


from django.db import connection

def department_reports(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        user = User.objects.get(userID=request.session['user_id'])
        dept = user.departmentid
        if not dept:
            return redirect('department:dashboard')

        # Get all teams and users in this department
        teams = Team.objects.filter(departmentid=dept)
        
        # Handle case when there are no teams
        if not teams.exists():
            return render(request, 'DeptLeadReports.html', {
                'teams': teams,
                'error_message': 'No teams found in your department.'
            })
            
        dept_users = User.objects.filter(teamid__in=teams)

        # Derive the last 30 days of 'sessions' based on voting dates
        today = date.today()
        month_ago = today - timedelta(days=30)
        
        # Get distinct dates when anyone voted - FIXED QUERY
        dates_qs = (Vote.objects
                    .filter(userid__in=dept_users,
                            votingdate__gte=month_ago)
                    .values_list('votingdate', flat=True)
                    .distinct()
                    .order_by('votingdate'))
        
        # Handle case when there are no votes
        if not dates_qs.exists():
            dates = []
            health_scores = []
        else:
            dates = [d.strftime('%b %d') for d in dates_qs]
            
            # Average health score per session date
            health_scores = []
            for d in dates_qs:
                avg = (Vote.objects
                       .filter(userid__in=dept_users,
                               votingdate=d)
                       .aggregate(a=Avg('votevalue'))['a'])
                health_scores.append(round(avg, 2) if avg is not None else 0)

        # Bar chart: average vote per team (overall)
        team_names, team_scores = [], []
        for t in teams:
            avg = (Vote.objects.filter(userid__teamid=t)
                   .aggregate(a=Avg('votevalue'))['a'] or 0)
            team_names.append(t.teamname)
            team_scores.append(round(avg, 2))

        # Overall metrics
        total_teams = teams.count()
        total_members = dept_users.count()
        total_votes = Vote.objects.filter(userid__in=dept_users).count()
        total_sessions = max(len(dates), 1)
        participation_rate = round(total_votes / (total_members * total_sessions) * 100, 1) if total_members > 0 else 0

        # Render template with JSON-encoded data
        return render(request, 'DeptLeadReports.html', {
            'total_teams': total_teams,
            'total_members': total_members,
            'participation_rate': participation_rate,
            'dates_json': json.dumps(dates),
            'health_scores_json': json.dumps(health_scores),
            'team_names_json': json.dumps(team_names),
            'team_scores_json': json.dumps(team_scores),
            'teams': teams,
            'active_page': 'reports', 
            'user': user,
        })

    except User.DoesNotExist:
        return redirect('login')

def get_data(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorised'}, status=401)

    view_type = request.GET.get('view')
    if view_type == 'teams':
        user = User.objects.filter(userID=request.session['user_id']).first()
        if user and user.departmentid:
            data = list(Team.objects.filter(departmentid=user.departmentid).values('teamid', 'teamname'))
        else:
            data = []
    else:
        data = []

    return JsonResponse(data, safe=False)


def view_summary(request, team_id):
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(userID=request.session['user_id'])

        if not user.departmentid:
            return render(request, 'DeptError.html', {'message': 'No department assigned to this user.'})

        team = get_object_or_404(Team, teamid=team_id, departmentid=user.departmentid)
        teams = Team.objects.filter(departmentid=user.departmentid)

        request.session['selected_team_id'] = team_id

        return render(request, 'DeptLeadVT.html', {
            'current_team': team,
            'teams': teams
        })

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
def departmentreport(request):
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
def department_metrics_api(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        user = User.objects.get(userID=request.session['user_id'])
        dept = user.departmentid
        if not dept:
            return JsonResponse({'error': 'No department assigned'}, status=400)
        
        # Get all teams in the department
        teams = Team.objects.filter(departmentid=dept)
        dept_users = User.objects.filter(teamid__in=teams)
        
        # Get votes from the last 30 days
        today = date.today()
        month_ago = today - timedelta(days=30)
        votes = Vote.objects.filter(
            userid__in=dept_users,
            votingdate__gte=month_ago
        )
        
        # Calculate average scores for each category
        categories = ['Teamwork', 'Mission', 'Speed', 'Delivering value']
        bar_metrics = {
            'categories': categories,
            'values': []
        }
        
        for category in categories:
            avg = votes.filter(cardid__cardname=category).aggregate(avg=Avg('votevalue'))['avg'] or 0
            bar_metrics['values'].append(round(avg, 2))
        
        # Line chart data (health score over time)
        dates_qs = votes.values_list('votingdate', flat=True).distinct().order_by('votingdate')
        line_metrics = {
            'labels': [d.strftime('%b %d') for d in dates_qs],
            'values': []
        }
        
        for d in dates_qs:
            avg = votes.filter(votingdate=d).aggregate(avg=Avg('votevalue'))['avg'] or 0
            line_metrics['values'].append(round(avg, 2))
        
        # Team comparison data
        team_data = []
        for team in teams:
            team_votes = votes.filter(userid__teamid=team)
            team_data.append({
                'name': team.teamname,
                'health': team_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0,
                'mission': team_votes.filter(cardid__cardname='Mission').aggregate(avg=Avg('votevalue'))['avg'] or 0,
                'fun': team_votes.filter(cardid__cardname='Fun').aggregate(avg=Avg('votevalue'))['avg'] or 0,
                'speed': team_votes.filter(cardid__cardname='Speed').aggregate(avg=Avg('votevalue'))['avg'] or 0,
                'value': team_votes.filter(cardid__cardname='Delivering value').aggregate(avg=Avg('votevalue'))['avg'] or 0
            })
        
        return JsonResponse({
            'summary': {
                'health_score': bar_metrics['values'][0],  # Using Teamwork as health score
                'mission': bar_metrics['values'][1],
                'fun': 0,  # You might need to add Fun category
                'speed': bar_metrics['values'][2],
                'value': bar_metrics['values'][3]
            },
            'bar_metrics': bar_metrics,
            'line_metrics': line_metrics,
            'teams': team_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
def team_metrics_api(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        team_id = request.GET.get('team')
        if not team_id:
            return JsonResponse({'error': 'Team ID required'}, status=400)
            
        team = Team.objects.get(teamid=team_id)
        team_users = User.objects.filter(teamid=team)
        
        # Get votes from last 30 days
        today = date.today()
        month_ago = today - timedelta(days=30)
        votes = Vote.objects.filter(
            userid__in=team_users,
            votingdate__gte=month_ago
        )
        
        # Calculate metrics
        metrics = {
            'health_score': round(votes.aggregate(avg=Avg('votevalue'))['avg'] or 0, 2),
            'mission_score': round(votes.filter(cardid__cardname='Mission').aggregate(avg=Avg('votevalue'))['avg'] or 0, 2),
            'fun_score': round(votes.filter(cardid__cardname='Fun').aggregate(avg=Avg('votevalue'))['avg'] or 0, 2),
            'speed_score': round(votes.filter(cardid__cardname='Speed').aggregate(avg=Avg('votevalue'))['avg'] or 0, 2),
            'value_score': round(votes.filter(cardid__cardname='Delivering value').aggregate(avg=Avg('votevalue'))['avg'] or 0, 2)
        }
        
        # Get historical data for line chart
        dates_qs = votes.values_list('votingdate', flat=True).distinct().order_by('votingdate')
        historical_data = {
            'labels': [d.strftime('%b %d') for d in dates_qs],
            'values': []
        }
        
        for d in dates_qs:
            avg = votes.filter(votingdate=d).aggregate(avg=Avg('votevalue'))['avg'] or 0
            historical_data['values'].append(round(avg, 2))
        
        return JsonResponse({
            'summary': metrics,
            'historical_data': historical_data,
            'team_name': team.teamname
        })
        
    except Team.DoesNotExist:
        return JsonResponse({'error': 'Team not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
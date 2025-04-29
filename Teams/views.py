
from django.shortcuts import render, redirect
from django.http import JsonResponse
from decimal import Decimal
from .models import Department, Team, Summary, Vote, Healthcheckcard, User
from django.db.models import Avg, Count, F, Q
from datetime import datetime, timedelta
import json



# Import your existing models here - update these model names to match your database schema
from .models import Department 
# If your models have different names, replace them with your actual model names



def getsenman_overview(request):
    departments = Department.objects.all()
    return render(request, 'SenManagerDash.html', {'departments': departments})


def getsenmanprogress(request):
    departments = Department.objects.all()
    teams = Team.objects.all()
    return render(request, 'SenManp2.html', {'departments': departments, 'teams': teams})


def department_summary(request):
    """
    View to render the department summary dashboard.
    Initially loads with the first department in the database.
    """
    # Get all departments for the dropdown
    departments = Department.objects.all().order_by('departmentname')
    
    # Default to first department if available
    default_department = departments.first() if departments.exists() else None
    
    context = {
        'departments': departments,
        'default_department': default_department,
    }
    
    return render(request, 'SenManagerp1.html', context)


def department_data(request):
    """
    API endpoint to get department data including teams and performance metrics.
    """
    dept_id = request.GET.get('dept')
    
    try:
        # Get the department
        department = Department.objects.get(departmentid=dept_id)
        
        # Get teams in this department
        teams = Team.objects.filter(departmentid=dept_id)
        
        # Calculate department metrics
        dept_metrics = calculate_department_metrics(department)
        
        # Get team metrics
        team_data = []
        for team in teams:
            team_metrics = calculate_team_metrics(team)
            team_data.append({
                'name': team.teamname,
                'health': team_metrics['health_score'],
                'mission': team_metrics['mission_score'],
                'speed': team_metrics['speed_score'],
                'value': team_metrics['value_score'],
                'trend': team_metrics['trend']
            })
        
        # Build trend data for last 6 months
        trend_data = get_trend_data(department)
        
        # Build radar chart data
        radar_data = get_radar_data(department)
        
        # Build summary data
        summary_data = get_summary_data(department)
        
        response_data = {
            'trends': trend_data,
            'radar': radar_data,
            'teams': team_data,
            'summary': summary_data
        }
        
        return JsonResponse(response_data)
        
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def calculate_department_metrics(department):
    """
    Calculate metrics for a department based on team data.
    """
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    
    # Get teams in this department
    teams = Team.objects.filter(departmentid=department.departmentid)
    
    # Get users in these teams
    users_in_dept = User.objects.filter(team__in=teams).distinct()
    
    # Get votes for users in this department
    current_votes = Vote.objects.filter(
        cardid__cardname__in=['Health', 'Mission', 'Speed', 'Value'],
        votingdate__gte=one_month_ago,
        userid__in=users_in_dept
    ).select_related('cardid')
    
    # Calculate average scores
    health_score = current_votes.filter(cardid__cardname='Health').aggregate(avg=Avg('votevalue'))['avg'] or 0
    mission_score = current_votes.filter(cardid__cardname='Mission').aggregate(avg=Avg('votevalue'))['avg'] or 0
    speed_score = current_votes.filter(cardid__cardname='Speed').aggregate(avg=Avg('votevalue'))['avg'] or 0
    value_score = current_votes.filter(cardid__cardname='Value').aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Calculate previous month's scores for trend
    two_months_ago = one_month_ago - timedelta(days=30)
    previous_votes = Vote.objects.filter(
        cardid__cardname__in=['Health', 'Mission', 'Speed', 'Value'],
        votingdate__gte=two_months_ago,
        votingdate__lt=one_month_ago,
        userid__in=users_in_dept
    ).select_related('cardid')
    
    prev_health_score = previous_votes.filter(cardid__cardname='Health').aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Calculate trends
    health_trend = round(health_score - prev_health_score, 1)
    
    return {
        'health_score': round(health_score, 1),
        'mission_score': round(mission_score, 1),
        'speed_score': round(speed_score, 1),
        'value_score': round(value_score, 1),
        'health_trend': health_trend
    }

def calculate_team_metrics(team):
    """
    Calculate metrics for a single team.
    """
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    two_months_ago = one_month_ago - timedelta(days=30)
    
    # Get votes for this team
    current_votes = Vote.objects.filter(
        cardid__cardname__in=['Health', 'Mission', 'Speed', 'Value'],
        votingdate__gte=one_month_ago,
        userid__in=User.objects.filter(team=team)  # Filter by users in this team
    ).select_related('cardid')
    
    # Calculate average scores
    health_score = current_votes.filter(cardid__cardname='Health').aggregate(avg=Avg('votevalue'))['avg'] or 0
    mission_score = current_votes.filter(cardid__cardname='Mission').aggregate(avg=Avg('votevalue'))['avg'] or 0
    speed_score = current_votes.filter(cardid__cardname='Speed').aggregate(avg=Avg('votevalue'))['avg'] or 0
    value_score = current_votes.filter(cardid__cardname='Value').aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Get previous month's health score
    previous_votes = Vote.objects.filter(
        cardid__cardname='Health',
        votingdate__gte=two_months_ago,
        votingdate__lt=one_month_ago,
        userid__in=User.objects.filter(team=team)  # Filter by users in this team
    )
    prev_health_score = previous_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Calculate trend
    trend = round(health_score - prev_health_score, 1)
    
    return {
        'health_score': round(health_score, 1),  # Make sure values are properly rounded
        'mission_score': round(mission_score, 1),
        'speed_score': round(speed_score, 1),
        'value_score': round(value_score, 1),
        'trend': trend
    }

def get_trend_data(department):
    """
    Get trend data for the department for the last 6 months.
    """
    today = datetime.now().date()
    
    # Get last 6 months
    months = []
    health_scores = []
    
    for i in range(5, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=i*30)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        month_name = month_start.strftime('%b')
        months.append(month_name)
        
        # Get teams in this department
        teams = Team.objects.filter(departmentid=department.departmentid)
        team_ids = [team.teamid for team in teams]
        
        # Get health scores for this month
        health_card = Healthcheckcard.objects.filter(cardname='Health').first()
        if health_card:
            month_votes = Vote.objects.filter(
                cardid=health_card.cardid,
                votingdate__gte=month_start,
                votingdate__lte=month_end
            )
            avg_score = month_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
            health_scores.append(round(avg_score, 2))
        else:
            health_scores.append(0)
    
    return {
        'months': months,
        'healthScores': health_scores
    }

def get_radar_data(department):
    """
    Get radar chart data for the department.
    """
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    
    # Get teams in this department
    teams = Team.objects.filter(departmentid=department.departmentid)
    team_ids = [team.teamid for team in teams]
    
    # Define categories
    categories = ['Mission', 'Plan', 'Speed', 'Value', 'Fun']
    scores = []
    
    # Get scores for each category
    for category in categories:
        card = Healthcheckcard.objects.filter(cardname=category).first()
        if card:
            category_votes = Vote.objects.filter(
                cardid=card.cardid,
                votingdate__gte=one_month_ago
            )
            avg_score = category_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
            scores.append(round(avg_score, 2))
        else:
            scores.append(0)
    
    return {
        'categories': categories,
        'scores': scores
    }

def get_summary_data(department):
    """
    Get summary data for the department.
    """
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    
    # Get teams in this department
    teams = Team.objects.filter(departmentid=department.departmentid)
    team_ids = [team.teamid for team in teams]
    
    # Get all votes for these teams
    votes = Vote.objects.filter(votingdate__gte=one_month_ago)
    
    # Count total votes
    total_votes = votes.count()
    
    # Get total users in the department
    users_in_teams = User.objects.filter(team__departmentid=department.departmentid).distinct()
    total_users = users_in_teams.count()
    
    # Calculate participation rate
    participation_rate = (total_votes / (total_users * 5)) * 100 if total_users > 0 else 0
    
    # Get last health check date
    last_vote = votes.order_by('-votingdate').first()
    last_check_date = last_vote.votingdate.strftime('%-d %b') if last_vote else 'N/A'
    
    return {
        'totalVotes': total_votes,
        'participationRate': round(participation_rate),
        'lastCheckDate': last_check_date
    }


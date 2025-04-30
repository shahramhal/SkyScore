
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
    teams = Team.objects.all()
    return render(request, 'SenManagerDash.html', {'departments': departments, 'teams': teams})


def getsenmanprogress(request):
    """
    View to render the Senior Manager progress page with necessary context.
    """
    # Get all departments for dropdown selection
    departments = Department.objects.all().order_by('departmentname')
    
    # Get all teams for reference
    teams = Team.objects.all().order_by('teamname')
    
    # Get department ID from URL parameter if available
    dept_id = request.GET.get('dept')
    
    # If department ID is provided, get that department, otherwise use the first one
    if dept_id:
        try:
            selected_department = Department.objects.get(departmentid=dept_id)
        except Department.DoesNotExist:
            selected_department = departments.first() if departments.exists() else None
    else:
        selected_department = departments.first() if departments.exists() else None
    
    # If we have a selected department, get its metrics
    if selected_department:
        dept_metrics = calculate_department_metrics(selected_department)
        dept_name = selected_department.departmentname
    else:
        dept_metrics = {
            'health_score': 0,
            'mission_score': 0,
            'speed_score': 0,
            'value_score': 0,
            'health_trend': 0
        }
        dept_name = "No Department Found"
    
    context = {
        'departments': departments,
        'teams': teams,
        'selected_department': selected_department,
        'department_name': dept_name,
        'health_score': dept_metrics['health_score'],
        'mission_score': dept_metrics['mission_score'],
        'speed_score': dept_metrics['speed_score'],
        'value_score': dept_metrics['value_score'],
    }
    
    return render(request, 'SenManp2.html', context)


def department_summary(request):
    """
    View to render the department summary dashboard.
    Initially loads with the first department in the database.
    """
    # Get all departments for the dropdown
    departments = Department.objects.all().order_by('departmentname')
    
    # Default to first department if available
    default_department = departments.first() if departments.exists() else None
    
    # Pass selected department's ID to template for initial load
    selected_dept_id = default_department.departmentid if default_department else None
    
    context = {
        'departments': departments,
        'default_department': default_department,
        'selected_dept_id': selected_dept_id,
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
                'id': team.teamid,
                'name': team.teamname,
                'health': team_metrics['health_score'],
                'mission': team_metrics['mission_score'],
                'speed': team_metrics['speed_score'],
                'value': team_metrics['value_score'],
                'trend': team_metrics['trend']
            })
        
        # Get trend data for last 6 months
        trend_data = get_trend_data(department)
        
        # Get radar data
        radar_data = get_radar_data(department)
        
        # Get summary data
        summary_data = get_summary_data(department)
        
        # Format data to match what the frontend expects
        response_data = {
            'department': {
                'id': department.departmentid,
                'name': department.departmentname,
            },
            # This matches the structure expected by updateDashboardData
            'summary': summary_data,
            'scores': {
                'health': dept_metrics['health_score'],
                'mission': dept_metrics['mission_score'],
                'speed': dept_metrics['speed_score'],
                'value': dept_metrics['value_score'],
                'healthTrend': dept_metrics['health_trend'],
                'missionTrend': 0.0,  # Placeholder values since we don't track these
                'speedTrend': 0.0,    # in the backend functions
                'valueTrend': 0.0
            },
            'trendData': {
                'labels': trend_data['months'],
                'values': trend_data['healthScores']
            },
            'performance': {
                'labels': radar_data['categories'],
                'values': radar_data['scores']
            },
            'teams': team_data
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
    
    # Get users in these teams - they belong to the department
    users_in_dept = User.objects.filter(departmentid=department.departmentid).distinct()
    
    # Get all health check cards
    health_card = Healthcheckcard.objects.filter(cardname='Health').first()
    mission_card = Healthcheckcard.objects.filter(cardname='Mission').first()
    speed_card = Healthcheckcard.objects.filter(cardname='Speed').first()
    value_card = Healthcheckcard.objects.filter(cardname='Value').first()
    
    # Get votes for users in this department for current month
    current_votes = Vote.objects.filter(
        votingdate__gte=one_month_ago,
        userid__in=users_in_dept
    ).select_related('cardid')
    
    # Calculate average scores
    health_score = current_votes.filter(cardid=health_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    mission_score = current_votes.filter(cardid=mission_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    speed_score = current_votes.filter(cardid=speed_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    value_score = current_votes.filter(cardid=value_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Calculate previous month's scores for trend
    two_months_ago = one_month_ago - timedelta(days=30)
    previous_votes = Vote.objects.filter(
        votingdate__gte=two_months_ago,
        votingdate__lt=one_month_ago,
        userid__in=users_in_dept
    ).select_related('cardid')
    
    prev_health_score = previous_votes.filter(cardid=health_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    
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
    
    # Get users in this team
    users_in_team = User.objects.filter(teamid=team.teamid)
    
    # Get all health check cards
    health_card = Healthcheckcard.objects.filter(cardname='Health').first()
    mission_card = Healthcheckcard.objects.filter(cardname='Mission').first()
    speed_card = Healthcheckcard.objects.filter(cardname='Speed').first()
    value_card = Healthcheckcard.objects.filter(cardname='Value').first()
    
    # Get votes for this team's users for current month
    current_votes = Vote.objects.filter(
        votingdate__gte=one_month_ago,
        userid__in=users_in_team
    ).select_related('cardid')
    
    # Calculate average scores
    health_score = current_votes.filter(cardid=health_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    mission_score = current_votes.filter(cardid=mission_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    speed_score = current_votes.filter(cardid=speed_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    value_score = current_votes.filter(cardid=value_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Get previous month's health score
    previous_votes = Vote.objects.filter(
        cardid=health_card,
        votingdate__gte=two_months_ago,
        votingdate__lt=one_month_ago,
        userid__in=users_in_team
    )
    prev_health_score = previous_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    # Calculate trend
    trend = round(health_score - prev_health_score, 1)
    
    return {
        'health_score': round(health_score, 1),
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
    
    # Get health card
    health_card = Healthcheckcard.objects.filter(cardname='Health').first()
    if not health_card:
        return {'months': [], 'healthScores': []}
    
    # Get users in this department
    users_in_dept = User.objects.filter(departmentid=department.departmentid).distinct()
    
    # Get last 6 months
    months = []
    health_scores = []
    
    for i in range(5, -1, -1):
        # Calculate start and end of month
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        if i > 0:
            next_month = month_start.replace(month=month_start.month+1) if month_start.month < 12 else month_start.replace(year=month_start.year+1, month=1)
            month_end = next_month - timedelta(days=1)
        else:
            month_end = today
        
        month_name = month_start.strftime('%b')
        months.append(month_name)
        
        # Get health scores for this month
        month_votes = Vote.objects.filter(
            cardid=health_card,
            votingdate__gte=month_start,
            votingdate__lte=month_end,
            userid__in=users_in_dept
        )
        
        avg_score = month_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
        health_scores.append(round(avg_score, 2))
    
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
    
    # Get users in this department
    users_in_dept = User.objects.filter(departmentid=department.departmentid).distinct()
    
    # Define categories
    categories = ['Mission', 'Health', 'Speed', 'Value', 'Fun']
    scores = []
    
    # Get scores for each category
    for category in categories:
        card = Healthcheckcard.objects.filter(cardname=category).first()
        if card:
            category_votes = Vote.objects.filter(
                cardid=card,
                votingdate__gte=one_month_ago,
                userid__in=users_in_dept
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
    
    # Get users in this department
    users_in_dept = User.objects.filter(departmentid=department.departmentid).distinct()
    total_users = users_in_dept.count()
    
    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()
    total_cards = health_cards.count()
    
    # Get all votes for users in this department in the last month
    votes = Vote.objects.filter(
        votingdate__gte=one_month_ago,
        userid__in=users_in_dept
    )
    
    # Count total votes
    total_votes = votes.count()
    
    # Calculate participation rate (total votes divided by possible votes)
    # Possible votes = users * cards
    possible_votes = total_users * total_cards
    participation_rate = (total_votes / possible_votes) * 100 if possible_votes > 0 else 0
    
    # Get last health check date
    last_vote = votes.order_by('-votingdate').first()
    last_check_date = last_vote.votingdate.strftime('%-d %b') if last_vote else 'N/A'
    
    # Get average health score
    health_card = Healthcheckcard.objects.filter(cardname='Health').first()
    health_votes = votes.filter(cardid=health_card) if health_card else votes.none()
    avg_health = health_votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
    
    return {
        'totalVotes': total_votes,
        'participationRate': round(participation_rate),
        'lastCheckDate': last_check_date,
        'averageHealth': round(avg_health, 1),
        'totalUsers': total_users,
        'totalTeams': Team.objects.filter(departmentid=department.departmentid).count()
    }

def team_lead_dashboard(request):
    teams = Team.objects.all()
    return render(request, 'TeamLeaderp1.html', { 'teams': teams})

def team_progress(request):
    teams = Team.objects.all()
    return render(request, 'TeamOverview.html', { 'teams': teams})


def engineering_metrics(request):
    """
    API endpoint to provide metrics data for the Engineering Operations Department.
    """
    try:
        # Get department ID from request or use default
        dept_id = request.GET.get('dept')
        if not dept_id:
            # Get the first department with "Engineering" in the name, or just the first one
            dept = Department.objects.filter(departmentname__icontains='Engineering').first()
            if not dept:
                dept = Department.objects.first()
            dept_id = dept.departmentid if dept else None

        if not dept_id:
            return JsonResponse({'error': 'No departments found'}, status=404)
            
        # Get the department
        department = Department.objects.get(departmentid=dept_id)
        
        # Calculate metrics for this department
        dept_metrics = calculate_department_metrics(department)
        
        # Get trend data for last 6 months
        trend_data = get_trend_data(department)
        
        # Get radar data
        radar_data = get_radar_data(department)
        
        # Format the data as expected by the frontend
        response_data = {
            'bar_metrics': {
                'categories': radar_data['categories'],
                'values': radar_data['scores']
            },
            'progression_data': {
                'dates': trend_data['months'],
                'mission': [3.8, 3.9, 4.0, 4.1, 4.0, 4.2],  # Placeholder, replace with actual data
                'plan': trend_data['healthScores'],  # Using health scores as plan for now
                'speed': [3.6, 3.7, 3.8, 3.9, 4.0, 4.1],  # Placeholder, replace with actual data
                'value': [3.9, 4.0, 4.1, 4.2, 4.3, 4.3]  # Placeholder, replace with actual data
            },
            'summary': {
                'health_score': dept_metrics['health_score'],
                'mission': dept_metrics['mission_score'],
                'fun': 3.95,  # Placeholder, replace with actual data if available
                'speed': dept_metrics['speed_score'],
                'value': dept_metrics['value_score']
            }
        }
        
        return JsonResponse(response_data)
        
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_settings_SM(request):
    return render(request, 'SenManSetting.html', {'active_page': 'settings'})

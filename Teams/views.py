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



from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg
from .models import Department, Team, User, Vote, Healthcheckcard
from datetime import date, timedelta

def getsenman_overview(request):
    departments = Department.objects.all()
    teams = Team.objects.all()
    return render(request, 'SenManagerDash.html', {'departments': departments, 'teams': teams})

def getsenmanprogress(request):
    departments = Department.objects.all()
    selected_dept_id = request.GET.get('dept')

    if selected_dept_id:
        try:
            selected_dept_id = int(selected_dept_id)
        except ValueError:
            selected_dept_id = departments.first().departmentid
    else:
        selected_dept_id = departments.first().departmentid

    return render(request, 'SenManp2.html', {
        'departments': departments,
        'selected_dept_id': selected_dept_id
    })


# Serve metrics data as JSON
def getsenmanager_metrics(request):
    try:
        dept_id = request.GET.get("dept")
        if not dept_id:
            return JsonResponse({"error": "No department ID provided"}, status=400)

        department = Department.objects.get(departmentid=dept_id)
        teams = Team.objects.filter(departmentid=department)
        users = User.objects.filter(teamid__in=teams)

        votes = Vote.objects.filter(userid__in=users, votingdate__gte=date.today() - timedelta(days=30))

        categories = ["Teamwork", "Learning", "Delivering value", "Mission", "Speed"]
        bar_values = []
        for name in categories:
            card = Healthcheckcard.objects.filter(cardname=name).first()
            avg = votes.filter(cardid=card).aggregate(avg=Avg("votevalue"))['avg'] or 0
            bar_values.append(round(avg, 2))

        progression_data = {
            "dates": [],
            "mission": [],
            "plan": [],
            "speed": [],
            "value": []
        }

        summary = {
            "health_score": round(sum(bar_values) / 5, 2),
            "mission": bar_values[3],  # Mission
            "fun": bar_values[1],      # Learning (repurposed as fun)
            "speed": bar_values[4],    # Speed
            "value": bar_values[2],    # Delivering value
        }

        return JsonResponse({
            "bar_metrics": {
                "categories": categories,
                "values": bar_values
            },
            "progression_data": progression_data,
            "summary": summary
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

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
        'active_page': 'health_cards',
    }
    
    return render(request, 'SenManagerp1.html', context)

def department_data(request):
    dept_id = request.GET.get('dept')

    try:
        department = Department.objects.get(departmentid=dept_id)
        teams = Team.objects.filter(departmentid=dept_id)

        # Calculate department-level metrics
        dept_metrics = calculate_department_metrics(department)
        summary_data = get_summary_data(department)
        trend_data = get_trend_data(department)
        radar_data = get_radar_data(department)

        # Team-level data
        team_data = []
        for team in teams:
            metrics = calculate_team_metrics(team)
            team_data.append({
                'id': team.teamid,
                'name': team.teamname,
                'health': metrics['health_score'],
                'mission': metrics['mission_score'],
                'speed': metrics['speed_score'],
                'value': metrics['value_score'],
                'trend': metrics['trend']
            })

        # Bar metrics for Category Score Overview chart
        categories = ["Teamwork", "Learning", "Delivering value", "Mission", "Speed"]
        users_in_dept = User.objects.filter(departmentid=department.departmentid).distinct()
        one_month_ago = datetime.now().date() - timedelta(days=30)
        votes = Vote.objects.filter(userid__in=users_in_dept, votingdate__gte=one_month_ago)

        bar_values = []
        for name in categories:
            card = Healthcheckcard.objects.filter(cardname=name).first()
            avg = votes.filter(cardid=card).aggregate(avg=Avg("votevalue"))["avg"] or 0
            bar_values.append(round(avg, 2))

        # Final JSON response structure
        response_data = {
            'department': {
                'id': department.departmentid,
                'name': department.departmentname,
            },
            'summary': summary_data,
            'scores': {
                'teamwork_score': dept_metrics['health_score'],
                'mission_score': dept_metrics['mission_score'],
                'speed_score': dept_metrics['speed_score'],
                'value_score': dept_metrics['value_score'],
                'health_trend': dept_metrics['health_trend'],
                'mission_trend': dept_metrics['missionTrend'],
                'speed_trend': dept_metrics['speedTrend'],
                'value_trend': dept_metrics['valueTrend'],
            },
            'bar_metrics': {
                'categories': categories,
                'values': bar_values
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
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)
    two_months_ago = one_month_ago - timedelta(days=30)

    users_in_dept = User.objects.filter(departmentid=department.departmentid).distinct()

    current_votes = Vote.objects.filter(
        votingdate__gte=one_month_ago,
        userid__in=users_in_dept
    ).select_related('cardid')

    previous_votes = Vote.objects.filter(
        votingdate__gte=two_months_ago,
        votingdate__lt=one_month_ago,
        userid__in=users_in_dept
    ).select_related('cardid')

    teamwork_card = Healthcheckcard.objects.filter(cardname='Teamwork').first()
    mission_card = Healthcheckcard.objects.filter(cardname='Mission').first()
    speed_card = Healthcheckcard.objects.filter(cardname='Speed').first()
    value_card = Healthcheckcard.objects.filter(cardname='Delivering value').first()

    teamwork_score = current_votes.filter(cardid=teamwork_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    mission_score = current_votes.filter(cardid=mission_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    speed_score = current_votes.filter(cardid=speed_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    value_score = current_votes.filter(cardid=value_card).aggregate(avg=Avg('votevalue'))['avg'] or 0

    prev_teamwork_score = previous_votes.filter(cardid=teamwork_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
    teamwork_trend = round(teamwork_score - prev_teamwork_score, 1)

    return {
        'health_score': round(teamwork_score, 1),  # shown as "Teamwork" on frontend
        'mission_score': round(mission_score, 1),
        'speed_score': round(speed_score, 1),
        'value_score': round(value_score, 1),
        'health_trend': teamwork_trend,
        'missionTrend': 0.0,
        'speedTrend': 0.0,
        'valueTrend': 0.0
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
    health_card = Healthcheckcard.objects.filter(cardname='Teamwork').first()
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
    health_card = Healthcheckcard.objects.filter(cardname='Teamwork').first()
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
    categories = ["Teamwork", "Learning", "Delivering value", "Mission", "Speed"]
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
    participation_rate = min((total_votes / possible_votes) * 100, 100) if possible_votes > 0 else 0
    
    # Get last health check date
    last_vote = votes.order_by('-votingdate').first()
    last_check_date = last_vote.votingdate.strftime('%d %b').lstrip("0").replace(" 0", " ") if last_vote else 'N/A'
    
    # Get average health score
    health_card = Healthcheckcard.objects.filter(cardname='Teamwork').first()
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

def get_category_trend(department, category_name):
    today = date.today()
    users = User.objects.filter(departmentid=department)

    card = Healthcheckcard.objects.filter(cardname=category_name).first()
    if not card:
        return []

    scores = []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        if i > 0:
            next_month = month_start.replace(month=month_start.month+1) if month_start.month < 12 else month_start.replace(year=month_start.year+1, month=1)
            month_end = next_month - timedelta(days=1)
        else:
            month_end = today

        votes = Vote.objects.filter(
            userid__in=users,
            cardid=card,
            votingdate__gte=month_start,
            votingdate__lte=month_end
        )
        avg = votes.aggregate(avg=Avg('votevalue'))['avg'] or 0
        scores.append(round(avg, 2))

    return scores

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

        # Calculate metrics
        dept_metrics = calculate_department_metrics(department)
        trend_data = get_trend_data(department)
        radar_data = get_radar_data(department)

        # Use the same categories defined in your radar
        categories = ["Teamwork", "Learning", "Delivering value", "Mission", "Speed"]
        users = User.objects.filter(teamid__departmentid=department)
        recent_votes = Vote.objects.filter(
            userid__in=users,
            votingdate__gte=date.today() - timedelta(days=30)
        )

        bar_values = []
        for name in categories:
            card = Healthcheckcard.objects.filter(cardname=name).first()
            avg = recent_votes.filter(cardid=card).aggregate(avg=Avg("votevalue"))["avg"] or 0
            bar_values.append(round(avg, 2))

        # Build response
        response_data = {
            
            'bar_metrics': {
                'categories': categories,
                'values': bar_values
            },
            'progression_data': {
                'dates': trend_data['months'],
                'mission': get_category_trend(department, 'Mission'),  # Can be extended to support real mission progression
                'plan': trend_data['healthScores'],
                'speed': get_category_trend(department, 'Speed'),    # Optional: implement get_speed_progression if needed
                'value': get_category_trend(department, 'Delivering value')     # Optional: implement get_value_progression if needed
            },
            'summary': {
                'health_score': round(sum(bar_values) / len(bar_values), 2),
                'mission': bar_values[3],
                'fun': bar_values[1],    # Learning = fun
                'speed': bar_values[4],
                'value': bar_values[2]
            }
        }

        return JsonResponse(response_data)

    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_settings_SM(request):
    return render(request, 'SenManSetting.html', {'active_page': 'settings'})

def debug_cards(request):
    card_names = list(Healthcheckcard.objects.values_list('cardname', flat=True))
    return JsonResponse({'cardnames': card_names})
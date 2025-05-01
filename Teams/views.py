from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
from .models import Department, Team, Summary, Vote, Healthcheckcard, User, Session
from django.db.models import Avg, Count, F, Q
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.contrib import messages



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
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)
    return render(request, 'SenManagerDash.html', {'departments': departments, 'teams': teams, 'user': user, 'active_page': 'senmanager_overview'})

def getsenmanprogress(request):
    departments = Department.objects.all()
    selected_dept_id = request.GET.get('dept')
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)

    if selected_dept_id:
        try:
            selected_dept_id = int(selected_dept_id)
        except ValueError:
            selected_dept_id = departments.first().departmentid
    else:
        selected_dept_id = departments.first().departmentid

    
    selected_department = Department.objects.get(departmentid=selected_dept_id)

    return render(request, 'SenManp2.html', {
        'departments': departments,
        'selected_dept_id': selected_dept_id,
        'selected_department': selected_department, 
        'user': user, 
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
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)
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
        'user': user,
    }
    
    return render(request, 'SenManagerp1.html', context )
def senman_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        # Get full user object from database
        user = User.objects.get(userID=request.session['user_id'])
        context = {
            'user': user,
            # Also pass session data to ensure it's available
            'session_data': request.session,
            'active_page': 'profile'
        }
        return render(request, 'senman_profile.html', context)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
def update_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            user = User.objects.get(userID=request.session['user_id'])
            
            # Update user information
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            
            '''''
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                # Delete old photo if exists
                if user.profile_photo:
                    if os.path.isfile(user.profile_photo.path):
                        default_storage.delete(user.profile_photo.path)
                
                # Save new photo
                photo = request.FILES['profile_photo']
                photo_name = f"profile_photos/user_{user.userID}_{photo.name}"
                user.profile_photo = photo_name
                default_storage.save(photo_name, ContentFile(photo.read()))
                
            # Handle photo removal
            if request.POST.get('remove_photo') == 'true' and user.profile_photo:
                if os.path.isfile(user.profile_photo.path):
                    default_storage.delete(user.profile_photo.path)
                user.profile_photo = None
                '''
            
            user.save()
            
            # Update session data if username changed
            if user.username != request.session.get('username'):
                request.session['username'] = user.username
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('senman_profile')
            
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('senman_profile')
    
    return redirect('senman_profile')


def change_password(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(userID=request.session['user_id'])
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Verify current password
            if user.password != current_password:
                messages.error(request, 'Current password is incorrect')
                return render(request, 'senman_change_password.html', {'user': user})
            
            # Verify new passwords match
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return render(request, 'senman_change_password.html', {'user': user})
            
            # Update password
            user.password = new_password
            user.save()
            
            messages.success(request, 'Password updated successfully!')
            return redirect('senman_profile')
            
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')
    
    try:
        user = User.objects.get(userID=request.session['user_id'])
        return render(request, 'senman_change_password.html', {'user': user})
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
    
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
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)
    return render(request, 'TeamLeaderp1.html', { 'teams': teams, 'active_page': 'team_lead_dashboard','user': user,})

    
def team_lead_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        # Get full user object from database
        user = User.objects.get(userID=request.session['user_id'])
        context = {
            'user': user,
            # Also pass session data to ensure it's available
            'session_data': request.session,
            'active_page': 'profile'
        }
        return render(request, 'team_lead_profile.html', context)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
def team_update_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            user = User.objects.get(userID=request.session['user_id'])
            
            # Update user information
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            
            '''''
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                # Delete old photo if exists
                if user.profile_photo:
                    if os.path.isfile(user.profile_photo.path):
                        default_storage.delete(user.profile_photo.path)
                
                # Save new photo
                photo = request.FILES['profile_photo']
                photo_name = f"profile_photos/user_{user.userID}_{photo.name}"
                user.profile_photo = photo_name
                default_storage.save(photo_name, ContentFile(photo.read()))
                
            # Handle photo removal
            if request.POST.get('remove_photo') == 'true' and user.profile_photo:
                if os.path.isfile(user.profile_photo.path):
                    default_storage.delete(user.profile_photo.path)
                user.profile_photo = None
                '''
            
            user.save()
            
            # Update session data if username changed
            if user.username != request.session.get('username'):
                request.session['username'] = user.username
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('team_lead_profile')
            
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('team_lead_profile')
    
    return redirect('team_lead_profile')

def team_lead_voting(request):
    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()

    # Get current user
    #
    if 'user_id' not in request.session:
        
         return HttpResponse("User not logged in.", status=401) 

    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)

    # Get active session
    current_session_date = timezone.now().date()
    active_session, created = Session.objects.get_or_create(
        sessiondate=current_session_date,
        defaults={
            'description': f"Health Check Session - {timezone.now().strftime('%B %Y')}"
        }
    )

    # Get user's votes for current session
    user_votes_current_session = Vote.objects.filter(
        userid=user, # Используем объект user
        votingdate=current_session_date
    )

    # Calculate progress based on user's votes in the current session
    votes_completed = user_votes_current_session.values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
        (votes_completed / total_cards * 100) if total_cards > 0 else 0,
        100
    )

    # Get the current card status for each card based on *user's* vote
    # Also calculate *user's* summary stats for the Card Summary section
    for card in health_cards:
        vote = user_votes_current_session.filter(cardid=card).first() 
        if vote:
            card.voted = True
            card.vote_value = vote.votevalue
            card.progress_status = vote.progressstatus
            
            card.green_count = 1 if vote.votevalue == 3 else 0
            card.amber_count = 1 if vote.votevalue == 2 else 0
            card.red_count = 1 if vote.votevalue == 1 else 0
        else:
            card.voted = False
            card.vote_value = None
            card.progress_status = None
            card.green_count = 0
            card.amber_count = 0
            card.red_count = 0

        
        total_user_votes_for_card = card.green_count + card.amber_count + card.red_count
        if total_user_votes_for_card > 0:
             card.green_percentage = (card.green_count / total_user_votes_for_card) * 100
             card.amber_percentage = (card.amber_count / total_user_votes_for_card) * 100
             card.red_percentage = (card.red_count / total_user_votes_for_card) * 100
        else:
             card.green_percentage = 0
             card.amber_percentage = 0
             card.red_percentage = 0


    
    user_voted_session_dates = Vote.objects.filter(userid=user).values_list('votingdate', flat=True).distinct()
    
    voting_sessions = Session.objects.filter(
        sessiondate__in=user_voted_session_dates
    ).order_by('-sessiondate')[:10] 

  
    for session in voting_sessions:
        session.user_vote_count = Vote.objects.filter(
            userid=user,
            votingdate=session.sessiondate
        ).count()

    # Get the first card as current_card if no card is selected
    current_card = health_cards.first() if health_cards.exists() else None

    context = {
        'user': user,
        'health_check_cards': health_cards,
        'active_session': active_session, 
        'voting_sessions': voting_sessions, 
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'current_card': current_card,
        'active_page': 'health_cards',
        'is_historical': False 
    }

    return render(request, 'teamvotingDashboard.html', context)
# Vote for a specific card

def team_lead_vote_card(request, card_id):
    
    
    # Get current user
    user = User.objects.get(userID=request.session['user_id'])
    
    # Get the current card
    current_card = get_object_or_404(Healthcheckcard, cardid=card_id)
    
    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()
    
    # Get active session
    active_session, created = Session.objects.get_or_create(
        sessiondate=timezone.now().date(),
        defaults={
            'description': f"Health Check Session - {timezone.now().strftime('%B %Y')}"
        }
    )
    
    # Get user's votes for this session
    user_votes = Vote.objects.filter(
        userid=user.userID,
        cardid__in=health_cards
        
    )
    
    # Calculate progress
    current_session_date = timezone.now().date()
    votes_completed = Vote.objects.filter(
        userid=user,
        votingdate=current_session_date
    ).values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
            (votes_completed / total_cards * 100) if total_cards > 0 else 0,
            100
        )
    
    # Get existing vote for this card if it exists
    existing_vote = Vote.objects.filter(
        userid=user.userID,
        cardid=current_card
    ).order_by('-votingdate').first()  # Show most recent vote
    
    # Find previous and next cards for navigation
    card_ids = list(health_cards.values_list('cardid', flat=True))
    current_index = card_ids.index(current_card.cardid) if current_card.cardid in card_ids else 0
    
    previous_card = None
    if current_index > 0:
        previous_card = health_cards.get(cardid=card_ids[current_index - 1])
    
    next_card = None
    if current_index < len(card_ids) - 1:
        next_card = health_cards.get(cardid=card_ids[current_index + 1])
    
    context = {
        'user': user,
        'current_card': current_card,
        'health_check_cards': health_cards,
        'existing_vote': existing_vote,
        'votes_completed': votes_completed,
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'has_previous': previous_card is not None,
        'previous_card': previous_card,
        'has_next': next_card is not None,
        'next_card': next_card,
        'active_session': active_session,
        'active_page': 'team_lead_voting'
    }
    
    return render(request, 'teamvotecard.html', context)
def team_lead_submit_vote(request, card_id):
    # if not request.user.is_authenticated or request.method != 'POST':
    #     return redirect('login')
    
    # Get current user and card

    # Get current user and card
    user = User.objects.get(userID=request.session['user_id'])
    current_card = get_object_or_404(Healthcheckcard, cardid=card_id)
    
    # Get form data
    vote_value = request.POST.get('voteValue')
    progress_status = request.POST.get('progressStatus')
    solutions = request.POST.get('solutions', '')
    comments = request.POST.get('comments', '')
    feedback = request.POST.get('feedback', '')
    
    # Create new vote 
    try:
        Vote.objects.create(
            userid=user,
            cardid=current_card,
            votevalue=vote_value,
            progressstatus=progress_status,
            comments=comments,
            votingdate=timezone.now().date(),
            # solutions=solutions,
            # feedback=feedback
        )
        messages.success(request, "Vote submitted successfully!")
    except Exception as e:
        messages.error(request, f"Error submitting vote: {str(e)}")
        return redirect('team_vote_card', card_id=card_id)
    
    # Handle navigation
    action = request.POST.get('action')
    health_check_cards = Healthcheckcard.objects.all()
    card_ids = list(health_check_cards.values_list('cardid', flat=True))
    current_index = card_ids.index(current_card.cardid) if current_card.cardid in card_ids else 0
    
    if action == 'next' and current_index < len(card_ids) - 1:
        next_card = health_check_cards.get(cardid=card_ids[current_index + 1])
        return redirect('team_vote_card', card_id=next_card.cardid)
    
    return redirect('team_voting_dashboard')
def start_new_session(request):
    # Create new session
    new_session = Session.objects.create(
        description=f"Health Check Session - {timezone.now().strftime('%B %d, %Y')}",
        sessiondate=timezone.now().date()
    )
    messages.success(request, "New voting session started!")
    return redirect('team_voting_dashboard')


def end_current_session(request):
    Session.objects.filter(is_active=True).update(is_active=False)
    messages.success(request, "Current voting session ended!")
    return redirect('engineer_dashboard')

def view_session(request, session_id):
    # Get the session
    session = get_object_or_404(Session, sessionid=session_id)

    # Get current user
    if 'user_id' not in request.session:
         return HttpResponse("User not logged in.", status=401)
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         return HttpResponse("User not found.", status=404)


    # Get all health check cards
    health_cards = Healthcheckcard.objects.all()

    # Get *user's* votes for this specific session
    user_votes_in_session = Vote.objects.filter(
        userid=user,
        votingdate=session.sessiondate
    ).select_related('cardid') 
    # Calculate progress for this user in this session
    votes_completed = user_votes_in_session.values('cardid').distinct().count()
    total_cards = health_cards.count()
    progress_percentage = min(
        (votes_completed / total_cards * 100) if total_cards > 0 else 0,
        100
    )

    # Get the card status for each card based on *user's* vote in this session
    # Also prepare data for the Card Summary section (showing user's vote)
    user_votes_dict = {vote.cardid_id: vote for vote in user_votes_in_session} 

    for card in health_cards:
        vote = user_votes_dict.get(card.cardid) 
        if vote:
            card.voted = True
            card.vote_value = vote.votevalue
            card.progress_status = vote.progressstatus
           
            card.green_count = 1 if vote.votevalue == 3 else 0
            card.amber_count = 1 if vote.votevalue == 2 else 0
            card.red_count = 1 if vote.votevalue == 1 else 0
        else:
            card.voted = False
            card.vote_value = None
            card.progress_status = None
            card.green_count = 0
            card.amber_count = 0
            card.red_count = 0

        total_user_votes_for_card = card.green_count + card.amber_count + card.red_count
        if total_user_votes_for_card > 0:
             card.green_percentage = (card.green_count / total_user_votes_for_card) * 100
             card.amber_percentage = (card.amber_count / total_user_votes_for_card) * 100
             card.red_percentage = (card.red_count / total_user_votes_for_card) * 100
        else:
             card.green_percentage = 0
             card.amber_percentage = 0
             card.red_percentage = 0

    # Get the first card as current_card if no card is selected
    current_card = health_cards.first() if health_cards.exists() else None

    context = {
        'user': user,
        'health_check_cards': health_cards,
        'active_session': session, 
        'user_session_votes': user_votes_in_session, 
        'votes_completed': votes_completed, 
        'total_cards': total_cards,
        'progress_percentage': progress_percentage,
        'current_card': current_card,
        'active_page': 'health_cards', 
        'is_historical': True 
    }

    return render(request, 'teamvotingDashboard.html', context)
    
def team_progress(request):

    
    # Get the current user's team
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)
    try:
        user = User.objects.get(userID=user_id)
        team = user.teamid
        
        # Calculate team metrics
        team_metrics = calculate_team_metrics(team)
        
        # Get team members
        team_members = User.objects.filter(teamid=team)
        
        # Get recent votes for visualization
        today = datetime.now().date()
        one_month_ago = today - timedelta(days=30)
        
        # Get all health check cards
        health_cards = Healthcheckcard.objects.all()
        
        # Get votes for the team in the last month
        votes = Vote.objects.filter(
            userid__in=team_members,
            votingdate__gte=one_month_ago
        ).select_related('cardid', 'userid')
        
        # Prepare data for charts
        categories = ["Teamwork", "Learning", "Delivering value", "Mission", "Speed"]
        category_scores = []
        
        for category in categories:
            card = health_cards.filter(cardname=category).first()
            if card:
                avg_score = votes.filter(cardid=card).aggregate(avg=Avg('votevalue'))['avg'] or 0
                category_scores.append(round(avg_score, 2))
            else:
                category_scores.append(0)
        
        # Get trend data for the last 3 months
        trend_data = {
            'dates': [],
            'scores': []
        }
        
        for i in range(3):
            month_start = today - timedelta(days=30 * (i + 1))
            month_end = today - timedelta(days=30 * i)
            month_votes = votes.filter(votingdate__gte=month_start, votingdate__lt=month_end)
            health_card = health_cards.filter(cardname='Teamwork').first()
            if health_card:
                avg_score = month_votes.filter(cardid=health_card).aggregate(avg=Avg('votevalue'))['avg'] or 0
                trend_data['dates'].append(month_start.strftime('%b %Y'))
                trend_data['scores'].append(round(avg_score, 2))
            else:
                trend_data['dates'].append(month_start.strftime('%b %Y'))
                trend_data['scores'].append(0)
        
        # Reverse the trend data to show oldest to newest
        trend_data['dates'].reverse()
        trend_data['scores'].reverse()
        
        context = {
            'team': team,
            'team_metrics': team_metrics,
            'team_members': team_members,
            'category_scores': {
                'categories': json.dumps(categories),
                'scores': json.dumps(category_scores)
            },
            'trend_data': {
                'dates': json.dumps(trend_data['dates']),
                'scores': json.dumps(trend_data['scores'])
            },
            'total_votes': votes.count(),
            'participation_rate': round((votes.count() / (len(team_members) * len(health_cards))) * 100),
            'user': user,
            'active_page': 'team_progress'
        }
        
        return render(request, 'TeamOverview.html', context)
        
    except User.DoesNotExist:
        return redirect('login')


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
    'department': {
        'id': department.departmentid,
        'name': department.departmentname
    },
    'bar_metrics': {
        'categories': categories,
        'values': bar_values
    },
    'progression_data': {
        'dates': trend_data['months'],
        'mission': get_category_trend(department, 'Mission'),
        'plan': trend_data['healthScores'],
        'speed': get_category_trend(department, 'Speed'),
        'value': get_category_trend(department, 'Delivering value')
    },
    'summary': {
        'health_score': round(sum(bar_values) / len(bar_values), 2),
        'mission': bar_values[3],
        'fun': bar_values[1],
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

def get_settings_TL(request):
    return render(request, 'Teamleadersetting.html', {'active_page': 'settings'})

def debug_cards(request):
    card_names = list(Healthcheckcard.objects.values_list('cardname', flat=True))
    return JsonResponse({'cardnames': card_names})

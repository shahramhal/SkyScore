
"""
Department/views.py
Department Lead dashboard and reporting with Chart.js visualisations.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse, HttpResponse
from Users.models import User, Vote  # assuming Vote.votingdate is a datetime
from Teams.models import Team
from datetime import timedelta, date
import json


def departmentDashboard(request):
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)
    teams = Team.objects.all()
    return render(request, 'DeptLeadpg2.html', {'teams': teams, 'user': user})






def department_settings(request):
    try:
        user = User.objects.get(userID=request.session['user_id'])
    except User.DoesNotExist:
         
         return HttpResponse("User not found.", status=404)
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'DeptLeadSetting.html',{'user': user})


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
    if 'user_id' not in request.session or 'selected_team_id' not in request.session:
        return redirect('login')

    try:
        team_id = request.session['selected_team_id']
        team = Team.objects.get(teamid=team_id)

        # Get all users in this team
        team_users = User.objects.filter(teamid=team)

        # Now fetch votes submitted by those users
        categories = ['Mission', 'Fun', 'Speed', 'Value']
        averages = {}
        for cat in categories:
            avg = Vote.objects.filter(userid__in=team_users, cardid__cardname=cat).aggregate(avg_vote=Avg('votevalue'))['avg_vote']
            averages[cat] = round(avg or 0, 2)

        return render(request, 'DeptLeadReports.html', {
            'team': team,
            'averages': averages
        })

    except Team.DoesNotExist:
        return render(request, 'DeptError.html', {'message': 'Selected team not found. Please go back and select again.'})
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
    team = get_object_or_404(Team, teamid=team_id)
    teams = Team.objects.all()
    return render(request, 'DeptLeadVT.html', {
        'current_team': team,
        'teams': teams
}   )
@login_required
def department_dashboard(request):
    """
    Show all teams in this department. Department Lead can then navigate
    to the reports page to see metrics.
    """
    # Fetch logged-in user
    user = User.objects.get(userID=request.session['user_id'])
    if not user.departmentid:
        # no department? kick back to login
        return redirect('login')

    # Only teams belonging to this department
    teams = Team.objects.filter(departmentid=user.departmentid)
    return render(request, 'DeptLeadpg2.html', {
        'teams': teams,

    })


@login_required
def department_reports(request):
    """
    Render health metrics for the selected team or for the whole department.
    We derive 'sessions' by distinct Vote.votingdate__date values.
    """
    user = User.objects.get(userID=request.session['user_id'])
    dept = user.departmentid
    if not dept:
        return redirect('department:dashboard')

    # Get all teams and users in this department
    teams = Team.objects.filter(departmentid=dept)
    dept_users = User.objects.filter(teamid__in=teams)

    # Derive the last 30 days of 'sessions' based on voting dates
    today = date.today()
    month_ago = today - timedelta(days=30)
    # Get distinct dates when anyone voted
    dates_qs = (Vote.objects
                .filter(userid__in=dept_users,
                        votingdate__date__gte=month_ago)
                .values_list('votingdate__date', flat=True)
                .distinct()
                .order_by('votingdate__date'))
    dates = [d.strftime('%b %d') for d in dates_qs]

    # Average health score per session date
    health_scores = []
    for d in dates_qs:
        avg = (Vote.objects
               .filter(userid__in=dept_users,
                       votingdate__date=d)
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
    participation_rate = round(total_votes / (total_members * total_sessions) * 100, 1)

    # Render template with JSON-encoded data
    return render(request, 'DeptLeadReports.html', {
        'total_teams': total_teams,
        'total_members': total_members,
        'participation_rate': participation_rate,
        'dates_json': json.dumps(dates),
        'health_scores_json': json.dumps(health_scores),
        'team_names_json': json.dumps(team_names),
        'team_scores_json': json.dumps(team_scores),
    })
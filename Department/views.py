"""
Department/views.py
Department Lead dashboard and reporting with Chart.js visualisations.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from Users.models import User, Vote  # assuming Vote.votingdate is a datetime
from Teams.models import Team
from datetime import timedelta, date
import json

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

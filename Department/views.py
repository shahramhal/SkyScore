from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from Teams.models import Team, User, Healthcheckcard, Vote
from django.db.models import Avg

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

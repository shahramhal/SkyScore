from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from Teams.models import Team, User

def departmentDashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        user = User.objects.get(userID=request.session['user_id'])

        # ✅ Filter teams only in user's department
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

def health_check_placeholder(request):
    return render(request, 'HealthCheckComingSoon.html')

def department_reports(request):
    return render(request, 'DeptReportsPlaceholder.html')

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

        return render(request, 'DeptLeadVT.html', {
            'current_team': team,
            'teams': teams
        })

    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')

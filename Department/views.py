from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from Teams.models import Team

def departmentDashboard(request):
    teams = Team.objects.all()
    return render(request, 'DeptLeadpg2.html', {'teams': teams})

def department_settings(request):
    return render(request, 'DeptLeadSetting.html')

def get_data(request):
    view_type = request.GET.get('view')
    if view_type == 'teams':
        data = list(Team.objects.values('id', 'name'))
    else:
        data = []
    return JsonResponse(data, safe=False)

def view_summary(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    teams = Team.objects.all()
    return render(request, 'DeptLeadVT.html', {
        'current_team': team,
        'teams': teams
    })

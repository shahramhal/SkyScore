from django.shortcuts import render

# Create your views here.
def teams(request):
    # Render the teams.html template when the /teams/ URL is accessed
    return render(request, 'DeptLeadpg2.html')

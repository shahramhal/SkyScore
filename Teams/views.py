from django.shortcuts import render

# Create your views here.



def SenManagerp1(request):
    return render(request, 'SenManagerDash.html' ) 
def get_departments(request):
    return render(request, 'get_departments.html' )
def get_department_data(request):
    return render(request, 'get_department_data.html' )
def get_settings(request):
    return render(request, 'SenManSetting.html' )

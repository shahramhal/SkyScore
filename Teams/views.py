from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg
import json
from decimal import Decimal
from .models import Department 


# Import your existing models here - update these model names to match your database schema
from .models import Department 
# If your models have different names, replace them with your actual model names



<<<<<<< HEAD
def getsenman_overview(request):
    departments = Department.objects.all()
    return render(request, 'SenManagerDash.html', {'departments': departments})
=======
def SenManagerp1(request):
    return render(request, 'SenManagerDash.html' ) 
def get_departments(request):
    return render(request, 'get_departments.html' )
def get_department_data(request):
    return render(request, 'get_department_data.html' )
def get_settings(request):
    return render(request, 'SenManSetting.html' )
>>>>>>> 7db597e2870cd9def8c2a55240fc87424d3bfc6a

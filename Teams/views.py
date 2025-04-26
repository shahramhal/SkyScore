from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg
import json
from decimal import Decimal
from .models import Department 


# Import your existing models here - update these model names to match your database schema
from .models import Department 
# If your models have different names, replace them with your actual model names



def getsenman_overview(request):
    departments = Department.objects.all()
    return render(request, 'SenManagerDash.html', {'departments': departments})

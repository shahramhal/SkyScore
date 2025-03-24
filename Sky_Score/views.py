# views.py at project level
from django.shortcuts import render

def guide(request):
    return render(request, 'guide.html')

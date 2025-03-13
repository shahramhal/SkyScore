from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def home(request):
    # Render the home page
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        # Get the username and password from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in and redirect to the dashboard
            login(request, user)
            return redirect('dashboard')
        else:
            # Display an error message if authentication fails
            messages.error(request, 'Invalid username or password')
    
    # Render the login page
    return render(request, 'login.html')

def signup_view(request):
    # Render the sign-up page
    return render(request, 'signup.html')

def admin_login(request):
    # Render the manager login page
    return render(request, 'admin_login.html')
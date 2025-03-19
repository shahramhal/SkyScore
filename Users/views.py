from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def home(request):
    # Render the home page
    return render(request, 'home.html')

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
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('userType', 'customer')  # Default to customer
        
        # Create a new user in your database
        user = user.objects.create(
            username=username,
            email=email,
            password=password,  # You should hash this!
            userType=user_type
        )
        
        # Create an auth user (if using Django's auth)
        # from django.contrib.auth.models import User as AuthUser
        # auth_user = AuthUser.objects.create_user(username=username, email=email, password=password)
        
        # Log the user in
        # login(request, auth_user)
        
        # Redirect to dashboard or login
        return redirect('login')
    
    # Render the sign-up page
    return render(request, 'signup.html')
def dashboard(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.userType == 'manager':  # Check if user is a manager
            login(request, user)
            return redirect('admin_dashboard')  # Redirect to admin dashboard
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
    
    # Render the manager login page
    return render(request, 'admin.html')
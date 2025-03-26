from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
# Create your views here.

def home(request):
    # Render the home page
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
         # Try to find the user in your custom table
        user = authenticate(request, username=username, password=password)
        
        try:
           
            
            # Store user info in session
            request.session['user_id'] = user.userID##
            request.session['user_type'] = user.userType
            request.session['username'] = user.username
            
            # Redirect based on user type
            if user.userType == 'Admin':
                return redirect('admin_dashboard') # !!!!!you should create template with this name 
            elif user.userType in ['SenManager', 'TeamLead']:
                return redirect('manager_dashboard')# !!!!!you should create template with this name)
            elif user.userType == 'Engineer':
                return redirect('engineer_dashboard')
            else:
                return redirect('home')
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    return render(request, 'login.html')
def signup_view(request):
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        role = request.POST.get('role')
        
        # Convert role from form to userType in database
        role_mapping = {
            'team_member': 'Engineer',
            'team_lead': 'TeamLead',
            'dept_lead': 'SenManager',
            'Sen-man': 'SenManager',
            'admin': 'Admin'
        }
        user_type = role_mapping.get(role, 'Engineer')  # Default to Engineer
        
         # Validate passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')
            
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')
        
        # Create a new user using Django's auth system
        try:
            # Create a new user using your custom User model
            user = User(
                username=username,
                email=email,
                password=make_password(password),  # Note: You should hash this password
                userType=user_type,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')
    
    # Render the sign-up page
    return render(request, 'signup.html')
def dashboard(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')


# def admin_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         # if user is not None and user.userType == 'manager':  # Check if user is a manager
#         #     login(request, user)
#         #     return redirect('admin_dashboard')  # Redirect to admin dashboard
#         # else:
#         #     messages.error(request, 'Invalid credentials or insufficient permissions')
    
#     # Render the manager login page
#     return render(request, 'admin_login.html')
def forgotPassword(request):
    return render (request, 'forgotPassword.html')
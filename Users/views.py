from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
# Create your views here.

def home(request):
    # Render the home page
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Try to find the user in your custom table
            user = User.objects.get(username=username, password=password)
            
            # Store user info in session
            request.session['user_id'] = user.userID
            request.session['user_type'] = user.userType
            request.session['username'] = user.username
            
            # Redirect based on user type
            if user.userType == 'Admin':
                return redirect('admin_dashboard') # !!!!!you should create template with this name 
            elif user.userType in ['SenManager', 'TeamLead']:
                return redirect('manager_dashboard')# !!!!!you should create template with this name)
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
        user_type = request.POST.get('userType', 'customer')  # Default to customer
        
        # Create a new user using Django's auth system
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,  # create_user handles hashing
                userType=user_type
            )
            
            # If you have a custom user profile model for user_type
            # Create it here and link to the auth user
            # profile = UserProfile.objects.create(user=user, user_type=user_type)
            
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
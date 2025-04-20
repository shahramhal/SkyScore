from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User                    
from django.contrib.auth import authenticate 
from .backends import CustomAuthBackend
from .backends import CustomPasswordResetTokenGenerator


from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    # Render the home page
    return render(request, 'home.html')

@never_cache
def login_view(request):
    
    if 'login_attempt' not in request.session:
        request.session.flush()
        request.session['login_attempt'] = True
        
    if 'user_id' in request.session:
        
        user_type = request.session.get('user_type')
        if user_type == 'Admin':
            return redirect('/admin/')
        if user_type in ['SenManager', 'TeamLead','DeptLead']:
            return redirect('engineer_dashboard')
        elif user_type == 'Engineer':
            return redirect('engineer_dashboard')
        else:
            return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
         # Try to find the user in your custom table
        user = authenticate(request, username=username, password=password)
        
        try:
           
            
            # Store user info in session
            request.session['user_id'] = user.userID
            request.session['user_type'] = user.userType
            request.session['username'] = user.username
            
            # Redirect based on user type
            if user.userType == 'Admin':
                return redirect('/admin/') # !!!!!you should create template with this name 
            elif user.userType in ['SenManager', 'TeamLead']:
                return redirect('engineer_dashboard')# !!!!!you should create template with this name)
            elif user.userType == 'Engineer':
                return redirect('engineer_dashboard')
            else:
                return redirect('home')
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    return render(request, 'login.html')
@never_cache
def signup_view(request):
    auth_backend = CustomAuthBackend()
    
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        role = request.POST.get('role')
        
         # Validate the input
        validation_errors=auth_backend.validate_signup(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            first_name=first_name,
            last_name=last_name,
            role=role
         )
       
        # If there are any errors, return to signup page with error messages
        if validation_errors:
            return render(request, 'signup.html', {
                'errors': validation_errors,
                'form_data': {
                    'username': username,
                    'email': email,
                    'name': first_name,
                    'surname': last_name,
                    'role': role
                }
            })
        
        # Create a new user using Django's auth system
        try:
            # Create a new user using your custom User model
            user = auth_backend.create_user(
                username=username,
                email=email,
                password=password,  # removed the hashing 
                userType=role,
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

password_reset_token_generator = CustomPasswordResetTokenGenerator()
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if the email exists
        try:
            user = User.objects.get(email=email)
            
            # Generate a unique token using custom token generator
            uidb64 = urlsafe_base64_encode(force_bytes(user.userID))
            token = password_reset_token_generator.make_token(user)
            
            # Build the reset URL
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uidb64}/{token}/"
            
            # Prepare email
            subject = 'Password Reset Request'
            
            # For simplicity, we'll use a plain text email here
            email_message = f"""
            Hello {user.first_name},
            
            You requested a password reset for your account. Please click the link below to reset your password:
            
            {reset_url}
            
            If you didn't request this, please ignore this email.
            
            Thank you,
            The Sky Score Team
            """
            
            # Send email
            try:
                send_mail(
                    subject,
                    email_message,
                    settings.EMAIL_HOST_USER,  # Use the configured email in settings
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
            
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
            return redirect('forgotPassword')
    
    return render(request, 'forgotPassword.html')

def resetPassword(request, uidb64, token):
    try:
        # Decode the user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(userID=uid)
        
        # Verify the token using custom token generator
        if password_reset_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'reset_password.html', {
                        'valid_token': True,
                        'uidb64': uidb64,
                        'token': token
                    })
                
                # Update the password
                user.password =new_password
                user.save()
                
                messages.success(request, 'Password has been reset successfully. You can now log in with your new password.')
                return redirect('login')
            
            return render(request, 'reset_password.html', {
                'valid_token': True,
                'uidb64': uidb64,
                'token': token
            })
        else:
            messages.error(request, 'The reset link is invalid or has expired.')
            return render(request, 'reset_password.html', {'valid_token': False})
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid reset link.')
        return render(request, 'reset_password.html', {'valid_token': False})

def passwordResetConfirm(request):
    messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
    return redirect('login')

@never_cache
# @login_required(login_url='login')
def engineer_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        # Get full user object from database
        user = User.objects.get(userID=request.session['user_id'])
        context = {
            'user': user,
            # Also pass session data to ensure it's available
            'session_data': request.session
        }
        return render(request, 'engineer_dashboard.html', context)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def logout_view(request):
    # Clear the session data
    request.session.flush()
    
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    # Redirect to login page
    messages.success(request, "You have been successfully logged out.")
    return response
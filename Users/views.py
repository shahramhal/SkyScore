from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User ,Healthcheckcard, Vote ,Department, Team                  
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
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone


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
        return redirect_by_UserType(user_type)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
         # Try to find the user in your custom table
        try:
            user = authenticate(request, username=username, password=password)
            if user is None:
                # If not found, check the custom User model
                messages.error(request, 'Please enter a valid username and password, or sign up for an account.')
                return redirect('login')
            
        except User.DoesNotExist:
            # If the user doesn't exist, show an error message
            messages.error(request, 'Invalid username or password')
            return redirect('login')   
        try:
           
            
            # Store user info in session
            request.session['user_id'] = user.userID
            request.session['user_type'] = user.userType
            request.session['username'] = user.username
            
            # Redirect based on user type
            return redirect_by_UserType(user.userType)
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    return render(request, 'login.html')

#This function handles the redirection based on user type
def redirect_by_UserType(user_type):
    # Redirect based on user type
   # Redirect to admin dashboard
    if user_type == 'SenManager':
        return redirect('SenManagerDash')  # Redirect to senior manager page
    elif user_type == 'TeamLead':
        return redirect('teamleaddash')  # Redirect to team leader dashboard
    elif user_type == 'DeptLead':
        return redirect('departmentDashboard')  # Redirect to department leader dashboard
    elif user_type == 'Engineer':
        return redirect('engineer_dashboard')  # Redirect to engineer dashboard
    else:
        return redirect('home')  # Default redirect for other user types
    

# Updated signup_view function for views.py
@never_cache
def signup_view(request):
    auth_backend = CustomAuthBackend()
    
    # Get departments and teams from database
    departments = Department.objects.all()
    teams = Team.objects.all()
    
    if request.method == 'POST':
        # Process the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        role = request.POST.get('role')
        department_id = request.POST.get('department')
        team_id = request.POST.get('team')
        
        # Determine if department/team are required based on role
        requires_dept = role in ['Engineer', 'team_lead', 'dept_lead']
        requires_team = role in ['Engineer', 'team_lead']
        
        # Validate the input
        validation_errors = auth_backend.validate_signup(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department_id if requires_dept else None,
            team=team_id if requires_team else None
        )
        
        # Add additional validation for department and team based on role
        if requires_dept and not department_id:
            if not validation_errors:
                validation_errors = {}
            validation_errors['department'] = 'Department is required for this role'
        
        if requires_team and not team_id:
            if not validation_errors:
                validation_errors = {}
            validation_errors['team'] = 'Team is required for this role'
       
        # If there are any errors, return to signup page with error messages
        if validation_errors:
            return render(request, 'signup.html', {
                'errors': validation_errors,
                'form_data': {
                    'username': username,
                    'email': email,
                    'name': first_name,
                    'surname': last_name,
                    'role': role,
                    'department': department_id,
                    'team': team_id
                },
                'departments': departments,
                'teams': teams
            })
        
        # Create a new user
        try:
            user = auth_backend.create_user(
                username=username,
                email=email,
                password=password,
                userType=auth_backend.map_role_to_user_type(role),  # Use the mapping function
                first_name=first_name,
                last_name=last_name
            )
            if not user:
                messages.error(request, "Error creating user account.")
                return render(request, 'signup.html', {
                    'form_data': {
                        'username': username,
                        'email': email,
                        'name': first_name,
                        'surname': last_name,
                        'role': role,
                        'department': department_id,
                        'team': team_id
                    },
                    'departments': departments,
                    'teams': teams
                })
                
            # Add department and team to user if provided and required by role
            if requires_dept and department_id:
                try:
                    department = Department.objects.get(departmentid=department_id)
                    user.departmentid = department
                except Department.DoesNotExist:
                    messages.warning(request, 'Selected department could not be assigned.')
            
            if requires_team and team_id:
                try:
                    team = Team.objects.get(teamid=team_id)
                    user.teamid = team
                except Team.DoesNotExist:
                    messages.warning(request, 'Selected team could not be assigned.')
            
            user.save()
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            
    # Render the sign-up page
    return render(request, 'signup.html', {
        'departments': departments,
        'teams': teams,
        'form_data': {}
    })


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
@never_cache
def engineer_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        # Get full user object from database
        user = User.objects.get(userID=request.session['user_id'])
        
        # Get health check cards with votes for this user
        health_cards = Healthcheckcard.objects.all()
        
        # For each card, check if the user has voted
        for card in health_cards:
            vote = Vote.objects.filter(userid=user, cardid=card).order_by('-votingdate').first()
            if vote is not None:
                card.voted = True
                card.vote_value = vote.votevalue
                card.progress_status = vote.progressstatus
                card.comments = vote.comments if vote.comments else ""
                card.last_voted = vote.votingdate
            else:
                card.voted = False
                card.vote_value = None
                card.progress_status = ""
                card.comments = ""
                card.last_voted = None
        
        current_session_date = timezone.now().date()
        votes_completed = Vote.objects.filter(
            userid=user,
            votingdate=current_session_date
        ).values('cardid').distinct().count()
        total_cards = health_cards.count()
        
        # Calculate percentage (capped at 100%)
        progress_percentage = min(
            (votes_completed / total_cards * 100) if total_cards > 0 else 0,
            100
        )

        context = {
            'user': user,
            'health_cards': health_cards,
            'total_cards': total_cards,
            'votes_completed': votes_completed,
            'progress_percentage': progress_percentage,
            'session_data': request.session,
            'active_page': 'dashboard'
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
@never_cache
def engineer_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        # Get full user object from database
        user = User.objects.get(userID=request.session['user_id'])
        context = {
            'user': user,
            # Also pass session data to ensure it's available
            'session_data': request.session,
            'active_page': 'profile'
        }
        return render(request, 'engineer_profile.html', context)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
def update_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            user = User.objects.get(userID=request.session['user_id'])
            
            # Update user information
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            
            '''''
            # Handle profile photo
            if 'profile_photo' in request.FILES:
                # Delete old photo if exists
                if user.profile_photo:
                    if os.path.isfile(user.profile_photo.path):
                        default_storage.delete(user.profile_photo.path)
                
                # Save new photo
                photo = request.FILES['profile_photo']
                photo_name = f"profile_photos/user_{user.userID}_{photo.name}"
                user.profile_photo = photo_name
                default_storage.save(photo_name, ContentFile(photo.read()))
                
            # Handle photo removal
            if request.POST.get('remove_photo') == 'true' and user.profile_photo:
                if os.path.isfile(user.profile_photo.path):
                    default_storage.delete(user.profile_photo.path)
                user.profile_photo = None
                '''
            
            user.save()
            
            # Update session data if username changed
            if user.username != request.session.get('username'):
                request.session['username'] = user.username
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('engineer_profile')
            
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('engineer_profile')
    
    return redirect('engineer_profile')

@never_cache
def change_password(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(userID=request.session['user_id'])
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Verify current password
            if user.password != current_password:
                messages.error(request, 'Current password is incorrect')
                return render(request, 'change_password.html', {'user': user})
            
            # Verify new passwords match
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return render(request, 'change_password.html', {'user': user})
            
            # Update password
            user.password = new_password
            user.save()
            
            messages.success(request, 'Password updated successfully!')
            return redirect('engineer_profile')
            
        except User.DoesNotExist:
            request.session.flush()
            return redirect('login')
    
    try:
        user = User.objects.get(userID=request.session['user_id'])
        return render(request, 'engineer_change_password.html', {'user': user})
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from .models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomAuthBackend(BaseBackend):
    # Convert role from form to userType in database
    ROLE_MAPPING= {
        'Engineer': 'Engineer',
        'team_lead': 'TeamLead',
        'dept_lead': 'SenManager',
        'Sen-man': 'SenManager',
        'admin': 'Admin'
    }
       
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Find the user with either the given username or email
            # The Q object allows for OR conditions in queries
            user = User.objects.get(Q(username=username) | Q(email=username))
            
            # Check the hashed password
            if user.password == password: #removed hashing  
                return user
            return None
        except User.DoesNotExist:
            return None
    
    def get_user(self,userID):
        try:
            return User.objects.get(pk=userID)
        except User.DoesNotExist:
            return None
        
    def validate_signup(self, username=None, email=None, password=None, confirm_password=None, first_name=None, last_name=None, role=None):
      
        errors = {}

        # Validate username
        if not username:
            errors['username'] = 'Username is required'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists'
        
        # Validate email
        if not email:
            errors['email'] = 'Email is required'
        elif not email or '@' not in email:
            errors['email'] = 'Invalid email format'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists'
        
        # Validate password
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        
        # Validate confirm password
        if not confirm_password:
            errors['confirm_password'] = 'Please confirm your password'
        elif password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        # Validate first name and last name
        if not first_name:
            errors['name'] = 'First name is required'
        if not last_name:
            errors['surname'] = 'Last name is required'
            
        return errors if errors else None
    def map_role_to_user_type(self, role):
        """
        Convert form role to database user type
        """
        return self.ROLE_MAPPING.get(role, 'Engineer')  # Default to Engineer
    def create_user(self, username,email, password, userType,first_name, last_name):
        """
        Create a new user with the given information
        """
        try :
            user =User(
                username=username,
                email=email,
                password=password,  
                userType=userType,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            return user
        except Exception as e:
            return None
        
class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, user, timestamp):
        # Create a unique hash using available fields
        return (
            str(user.userID) + 
            str(timestamp) + 
            str(user.password)
        )

# Create an instance of the custom token generator
password_reset_token_generator = CustomPasswordResetTokenGenerator()
       
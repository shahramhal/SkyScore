from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from .models import User, Department, Team
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomAuthBackend(BaseBackend):
    # Convert role from form to userType in database
    ROLE_MAPPING= {
        'Engineer': 'Engineer',
        'team_lead': 'TeamLead',
        'dept_lead': 'DeptLead',  # Updated to match the required role 
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
        
    def validate_signup(self, username=None, email=None, password=None, confirm_password=None, first_name=None, last_name=None, role=None, department=None, team=None):
      
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
        
        # Validate role
        if not role:
            errors['role'] = 'Role is required'
        elif role not in self.ROLE_MAPPING:
            errors['role'] = 'Invalid role selected'
        
        # Role-specific validations
        if role in ['Engineer', 'team_lead', 'dept_lead'] and department is None:
            errors['department'] = 'Department is required for this role'
            
        if role in ['Engineer', 'team_lead'] and team is None:
            errors['team'] = 'Team is required for this role'
            
        return errors if errors else None
    def map_role_to_user_type(self, role):
        """
        Convert form role to database user type
        """
        return self.ROLE_MAPPING.get(role, 'Engineer')  # Default to Engineer
    def create_user(self, username, email, password, userType, first_name, last_name, department=None, team=None):
        """
        Create a new user with the given information
        """
        try:
            user = User(
                username=username,
                email=email,
                password=password,  
                userType=userType,
                first_name=first_name,
                last_name=last_name
            )
            
            # Save first to get an ID
            user.save()
            
            # Then associate department and team if provided
            if department:
                try:
                    dept_obj = Department.objects.get(departmentid=department)
                    user.departmentid = dept_obj
                except Department.DoesNotExist:
                    pass
    
            if team:
                try:
                    team_obj = Team.objects.get(teamid=team)
                    user.teamid = team_obj
                except Team.DoesNotExist:
                    pass
            
            # Save again with the relationships
            user.save()
            return user
        except Exception as e:
            print(f"Error creating user: {str(e)}")
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
       
from django.contrib.auth.backends import BaseBackend
from .models import User

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Find the user with the given username
            user = User.objects.get(username=username)
            
            # Check the password - you might need to handle hashing depending on how your passwords are stored
            if user.password == password:  # Use proper password verification if passwords are hashed
                return user
            return None
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
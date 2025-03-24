from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from .models import User

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Find the user with either the given username or email
            # The Q object allows for OR conditions in queries
            user = User.objects.get(Q(username=username) | Q(email=username))
            
            # Check the hashed password
            if check_password(password, user.password):
                return user
            return None
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
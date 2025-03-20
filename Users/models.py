
from django.db import models

class User(models.Model):
    userID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    userType = models.CharField(max_length=50)
    managerID = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        # This tells Django this model maps to an existing table
        db_table = 'User'
        # If you have multiple apps, you might need to specify which app this model belongs to
        # app_label = 'your_app_name'
    
    def __str__(self):
        return self.username
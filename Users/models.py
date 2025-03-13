from django.db import models

class User(models.Model):
    userID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)  # In a real app, you'd use Django's auth system instead
    userType = models.CharField(max_length=50) 
    managerID = models.IntegerField(null=True, blank=True)  # Allow NULL values
    
    def __str__(self):
        return self.username
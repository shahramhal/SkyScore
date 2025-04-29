from django.db import models


# Create your models here.

class User(models.Model):
    userid = models.AutoField(db_column='userID', primary_key=True, blank=True)  # Field name made lowercase.
    username = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    usertype = models.TextField(db_column='userType', blank=True, null=True)  # Field name made lowercase.
    managerid = models.ForeignKey('self', models.DO_NOTHING, db_column='managerID', blank=True, null=True)  # Field name made lowercase.
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'User'

  
class Department(models.Model):
    departmentid = models.AutoField(db_column='departmentID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    departmentname = models.TextField(db_column='departmentName', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = False
        db_table = 'Department'
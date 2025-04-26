from django.db import models


# Create your models here.

    
class Department(models.Model):
    departmentid = models.AutoField(db_column='departmentID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    departmentname = models.TextField(db_column='departmentName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Department'
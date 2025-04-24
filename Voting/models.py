from django.db import models

# Create your models here.

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
class Healthcheckcard(models.Model):
    cardid = models.AutoField(db_column='cardID', primary_key=True)  # Field name made lowercase.
    cardname = models.TextField(db_column='cardName', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HealthCheckCard'
        
    def __str__(self):  # Fixed the typo in _str__ -> __str__
        return self.cardname

class Vote(models.Model):
    voteid = models.AutoField(db_column='voteID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    cardid = models.ForeignKey(Healthcheckcard, models.DO_NOTHING, db_column='cardID', blank=True, null=True)  # Field name made lowercase.
    votevalue = models.IntegerField(db_column='voteValue', blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Vote'

    def __str__(self):
        return f"Vote {self.voteid} by {self.userid.username} on {self.cardid.cardname}"

class Session(models.Model):
    sessionid = models.AutoField(db_column='sessionID', primary_key=True)  # Field name made lowercase.
    voteid = models.ForeignKey('Vote', models.DO_NOTHING, db_column='voteID', blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    sessiondate = models.DateField(db_column='sessionDate', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Session'
        
    def __str__(self):
        return f"Session {self.sessionid} on {self.sessiondate}"
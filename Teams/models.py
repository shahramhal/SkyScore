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
    teamid=models.ForeignKey('Team', models.DO_NOTHING, db_column='teamID', blank=True)  # Field name made lowercase.
    departmentid=models.ForeignKey('Department', models.DO_NOTHING, db_column='departmentID', blank=True,)  # Field name made lowercase.
    
    
    

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

class Team(models.Model):
    teamid = models.AutoField(db_column='teamID', primary_key=True, blank=True)  # Field name made lowercase.
    voteid = models.ForeignKey('Vote', models.DO_NOTHING, db_column='voteID', blank=True, null=True)  # Field name made lowercase.
    summaryid = models.ForeignKey('Summary', models.DO_NOTHING, db_column='summaryID', blank=True)  # Field name made lowercase.
    teamname = models.TextField(db_column='teamName', blank=True, null=True)  # Field name made lowercase.
    departmentid = models.ForeignKey('Department', models.DO_NOTHING, db_column='departmentID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Team'

    def __str__(self):
        return str(self.teamname)

class Summary(models.Model):
    summaryid = models.AutoField(db_column='summaryID', primary_key=True, )  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    averagevote = models.FloatField(db_column='averageVote', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Summary'

class Vote(models.Model):
    voteid = models.AutoField(db_column='voteID', primary_key=True, blank=True,)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='userID', blank=True, )  # Field name made lowercase.
    cardid = models.ForeignKey('Healthcheckcard', models.DO_NOTHING, db_column='cardID', blank=True, )  # Field name made lowercase.
    votevalue = models.IntegerField(db_column='voteValue', blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    comments = models.TextField(blank=True, null=True)
    votingdate = models.DateField(db_column='voting_date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Vote'

class Healthcheckcard(models.Model):
    cardid = models.AutoField(db_column='cardID', primary_key=True, blank=True,)  # Field name made lowercase.
    cardname = models.TextField(db_column='cardName', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    last_updated = models.DateField(db_column='last_update', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = False
        db_table = 'HealthCheckCard'
class Session(models.Model):
    sessionid = models.AutoField(db_column='sessionID', primary_key=True)
    sessiondate = models.DateField(db_column='sessionDate', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Session'

    def __str__(self):
        return f"Session {self.sessionid} on {self.sessiondate}"
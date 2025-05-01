from django.db import models

class Team(models.Model):
    teamid = models.AutoField(db_column='teamID', primary_key=True, blank=True,)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    voteid = models.ForeignKey('Vote', models.DO_NOTHING, db_column='voteID', blank=True, null=True)  # Field name made lowercase.
    summaryid = models.ForeignKey('Summary', models.DO_NOTHING, db_column='summaryID', blank=True, null=True)  # Field name made lowercase.
    teamname = models.TextField(db_column='teamName', blank=True, null=True)  # Field name made lowercase.
    departmentid = models.ForeignKey('Department', models.DO_NOTHING, db_column='departmentID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Team'
class Summary(models.Model):
    summaryid = models.AutoField(db_column='summaryID', primary_key=True, blank=True,)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    averagevote = models.FloatField(db_column='averageVote', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Summary'

class Vote(models.Model):
    voteid = models.AutoField(db_column='voteID', primary_key=True, blank=True, )  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, )  # Field name made lowercase.
    cardid = models.ForeignKey('Healthcheckcard', models.DO_NOTHING, db_column='cardID', blank=True, )  # Field name made lowercase.
    votevalue = models.IntegerField(db_column='voteValue', blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    comments = models.TextField(blank=True, null=True)
    votingdate = models.DateField(db_column='voting_date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Vote'
class Healthcheckcard(models.Model):
    cardid = models.AutoField(db_column='cardID', primary_key=True, blank=True, )  # Field name made lowercase.
    cardname = models.TextField(db_column='cardName', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    last_updated = models.DateField(db_column='last_update', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = False
        db_table = 'HealthCheckCard'
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
        db_table = 'Users'
    def __str__(self):
        return self.username
class Department(models.Model):
    departmentid = models.AutoField(db_column='departmentID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, )  # Field name made lowercase.
    departmentname = models.TextField(db_column='departmentName', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = False
        db_table = 'Department'

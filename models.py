# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Department(models.Model):
    departmentid = models.AutoField(db_column='departmentID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    departmentname = models.TextField(db_column='departmentName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Department'


class Healthcheckcard(models.Model):
    cardid = models.AutoField(db_column='cardID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    cardname = models.TextField(db_column='cardName', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HealthCheckCard'


class Session(models.Model):
    sessionid = models.AutoField(db_column='sessionID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    voteid = models.ForeignKey('Vote', models.DO_NOTHING, db_column='voteID', blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    sessiondate = models.DateField(db_column='sessionDate', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Session'


class Summary(models.Model):
    summaryid = models.AutoField(db_column='summaryID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    averagevote = models.FloatField(db_column='averageVote', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Summary'


class Team(models.Model):
    teamid = models.AutoField(db_column='teamID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    voteid = models.ForeignKey('Vote', models.DO_NOTHING, db_column='voteID', blank=True, null=True)  # Field name made lowercase.
    summaryid = models.ForeignKey(Summary, models.DO_NOTHING, db_column='summaryID', blank=True, null=True)  # Field name made lowercase.
    teamname = models.TextField(db_column='teamName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Team'


class User(models.Model):
    userid = models.AutoField(db_column='userID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    username = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    usertype = models.TextField(db_column='userType', blank=True, null=True)  # Field name made lowercase.
    managerid = models.ForeignKey('self', models.DO_NOTHING, db_column='managerID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'


class UsertypeHealthcheckcardAlloc(models.Model):
    userid = models.OneToOneField(User, models.DO_NOTHING, db_column='userID', primary_key=True, blank=True, null=True)  # Field name made lowercase. The composite primary key (userID, sessionID) found, that is not supported. The first column is selected.
    sessionid = models.ForeignKey(Session, models.DO_NOTHING, db_column='sessionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'UserType_HealthCheckCard_Alloc'


class UsertypeSessionAlloc(models.Model):
    userid = models.OneToOneField(User, models.DO_NOTHING, db_column='userID', primary_key=True, blank=True, null=True)  # Field name made lowercase. The composite primary key (userID, sessionID) found, that is not supported. The first column is selected.
    sessionid = models.ForeignKey(Session, models.DO_NOTHING, db_column='sessionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'UserType_Session_Alloc'


class Vote(models.Model):
    voteid = models.AutoField(db_column='voteID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    cardid = models.ForeignKey(Healthcheckcard, models.DO_NOTHING, db_column='cardID', blank=True, null=True)  # Field name made lowercase.
    votevalue = models.IntegerField(db_column='voteValue', blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Vote'



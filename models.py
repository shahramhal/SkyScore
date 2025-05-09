# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Department(models.Model):
    departmentid = models.AutoField(db_column='departmentID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    departmentname = models.TextField(db_column='departmentName', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = False
        db_table = 'Department'


class Healthcheckcard(models.Model):
    cardid = models.AutoField(db_column='cardID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
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

class Summary(models.Model):
    summaryid = models.AutoField(db_column='summaryID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    averagevote = models.FloatField(db_column='averageVote', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Summary'


class SummarySessionAlloc(models.Model):
    summaryid = models.ForeignKey(Summary, models.DO_NOTHING, db_column='SummaryID', to_field='SummaryID', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.ForeignKey(Session, models.DO_NOTHING, db_column='SessionID', to_field='SessionID', blank=True, null=True)  # Field name made lowercase.
    period = models.TextField(db_column='Period', primary_key=True, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Summary_Session_Alloc'


class Team(models.Model):
    teamid = models.AutoField(db_column='teamID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    voteid = models.ForeignKey('Vote', models.DO_NOTHING, db_column='voteID', blank=True, null=True)  # Field name made lowercase.
    summaryid = models.ForeignKey(Summary, models.DO_NOTHING, db_column='summaryID', blank=True, null=True)  # Field name made lowercase.
    teamname = models.TextField(db_column='teamName', blank=True, null=True)  # Field name made lowercase.
    departmentid = models.ForeignKey('Department', models.DO_NOTHING, db_column='departmentID', blank=True, null=True)  # Field name made lowercase.

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
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)

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


class UsersUser(models.Model):
    userid = models.AutoField(db_column='userID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    password = models.CharField(max_length=100)
    usertype = models.CharField(db_column='userType', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Users_user'


class Vote(models.Model):
    voteid = models.AutoField(db_column='voteID', primary_key=True, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='userID', blank=True, null=True)  # Field name made lowercase.
    cardid = models.ForeignKey(Healthcheckcard, models.DO_NOTHING, db_column='cardID', blank=True, null=True)  # Field name made lowercase.
    votevalue = models.IntegerField(db_column='voteValue', blank=True, null=True)  # Field name made lowercase.
    progressstatus = models.TextField(db_column='progressStatus', blank=True, null=True)  # Field name made lowercase.
    comments = models.TextField(blank=True, null=True)
    votingdate = models.DateField(db_column='voting_date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Vote'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

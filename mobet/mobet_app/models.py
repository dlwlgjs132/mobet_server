from django.db import models
import os
import datetime
from django_pandas.managers import DataFrameManager

# Create your models here.
class User(models.Model):
    USERID = models.CharField(max_length=30, blank=False, default='',unique=True)
    USERUID = models.CharField(max_length=50, blank=False, default='',unique=True)
    PHONENUM = models.CharField(max_length=20, default='', unique=True)
    NICKNAME = models.CharField(max_length=10, blank=False, default='',unique=True)
    RECENTPAYAVG = models.IntegerField(null=True)
    SIGNUPDATE = models.DateTimeField(auto_now_add=True)
    PROFILEIMG = models.CharField(max_length=100, blank=False, default='', null=True)
    TIMELOG = models.DateTimeField(null=True)

    objects = DataFrameManager()

    def __int__(self):
        return self.pk

class userRank(models.Model):
    USER_ID = models.ForeignKey(
        User,
        related_name='user_rank',
        on_delete=models.CASCADE
    )
    GRADE = models.CharField(max_length=5, blank=False, default='C')
    POINTS = models.IntegerField(default=500)
    WINRECORD = models.IntegerField(default=0)
    GAMECOUNT = models.IntegerField(default=0)

    objects = DataFrameManager()

    class Meta:
        ordering = ('-POINTS',)
    
    
class categoryList(models.Model):
    CATEGORY = models.CharField(max_length=20, unique=True)

    objects = DataFrameManager()

    class Meta:
        ordering = ('CATEGORY',)

    def __int__(self):
        return self.pk
    
class financeInfo(models.Model):
    USER_ID = models.ForeignKey(
        User,
        related_name='finance',
        on_delete=models.CASCADE
    )
    CATEGORYCODE = models.ForeignKey(
        categoryList,
        related_name='finance',
        on_delete=models.CASCADE
    )
    STORE = models.CharField(max_length=20, null=True)
    PAYMENTTIME = models.DateTimeField()
    PAYMENTPRICE = models.IntegerField()
    INANDOUT = models.BooleanField(default=True)

    objects = DataFrameManager()

    class Meta:
        ordering = ('PAYMENTTIME',)
    
class competitionSet(models.Model):
    ROOMNAME = models.CharField(max_length=30, blank=False, default='')
    OWNER_ID = models.ForeignKey(
        User,
        related_name='competition',
        on_delete=models.SET_NULL,
        null=True
    )
    STARTDATE = models.DateTimeField()
    DUEDATE = models.DateTimeField()
    CATEGORYCODE = models.ForeignKey(
        categoryList,
        related_name='competition',
        on_delete=models.CASCADE,
    )
    SETTINGMONEY = models.IntegerField()
    RECENTPAYAVGMIN = models.IntegerField(null=True)
    RECENTPAYAVGMAX = models.IntegerField(null=True)
    OPEN = models.BooleanField(default=True)
    IS_FINISHED = models.BooleanField(default=False)

    objects = DataFrameManager()

    def __int__(self):
        return self.pk

class Notification(models.Model):
    OWNER_ID = models.ForeignKey(
        User,
        related_name='notification',
        on_delete=models.CASCADE
    )
    ROOMNAME = models.ForeignKey(
        competitionSet,
        related_name='notification',
        on_delete=models.CASCADE,
        null=True
    )
    USER_ID = models.ForeignKey(
        User,
        related_name='notification_user',
        on_delete=models.CASCADE
    )
    ALARM = models.BooleanField(default=False)


    objects = DataFrameManager()

    class Meta:
        ordering = ('OWNER_ID',)

class participatedList(models.Model):
    ROOMNUM_ID = models.ForeignKey(
        competitionSet,
        related_name='participated',
        on_delete=models.CASCADE
    )
    USER_ID = models.ForeignKey(
        User,
        related_name='participated',
        on_delete=models.CASCADE
    )
    LEFTMONEY = models.IntegerField()
    TIMELOG = models.DateTimeField(null=True)

    objects = DataFrameManager()

    class Meta:
        ordering = ('ROOMNUM_ID','-LEFTMONEY')

class userGameRecord(models.Model):
    ROOMNUM_ID = models.ForeignKey(
        competitionSet,
        related_name='game_record',
        on_delete=models.CASCADE
    )
    USER_ID = models.ForeignKey(
        User,
        related_name='game_record',
        on_delete=models.CASCADE
    )
    SUCCESSES = models.BooleanField(default=False)
    RECORDDATE = models.DateTimeField(auto_now=True)
    GAMEGRADE = models.IntegerField(default=1)
    LEFTMONEY = models.IntegerField()

    objects = DataFrameManager()

    class Meta:
        ordering = ('ROOMNUM_ID', 'GAMEGRADE',)

class Relationship(models.Model):
    USERONE = models.ForeignKey(
        User,
        related_name='relationship_one',
        on_delete=models.CASCADE
    )
    USERTWO = models.ForeignKey(
        User,
        related_name='relationship_two',
        on_delete=models.CASCADE
    )

    objects = DataFrameManager()

    class Meta:
        ordering = ('USERONE',)

class Test(models.Model):
    test = models.IntegerField()

class Image(models.Model):
        image = models.ImageField(upload_to='usr')
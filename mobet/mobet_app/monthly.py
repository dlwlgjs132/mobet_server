from django.shortcuts import render
from mobet_app.models import User
from mobet_app.models import financeInfo
from mobet_app.models import participatedList
from mobet_app.models import competitionSet
from mobet_app.models import userGameRecord
from mobet_app.models import userRank
from django.utils import timezone

from collections import Counter
from collections import deque
import operator
from datetime import datetime
import datetime
import re
import math
from pandas import Series

from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django_pandas.io import read_frame
import pandas as pd
from dateutil.relativedelta import relativedelta


user = User.objects.all()
financeinfo = financeInfo.objects.all()
participatedlist = participatedList.objects.all()
competitionset = competitionSet.objects.all()
usergamerecord = userGameRecord.objects.all()
userrank = userRank.objects.all()
userrankdf = read_frame(userrank, fieldnames=['GRADE', 'WINRECORD', 'GAMECOUNT', 'POINTS', 'USER_ID_id'])

thisTime = timezone.now()

class Monthly:
    def __init__(self,thisPlayer):
        self.thisPlayer=thisPlayer
        self.onemonth = thisTime - relativedelta(months=1)
        self.twomonth = thisTime - relativedelta(months=2)
        self.threemonth = thisTime - relativedelta(months=3)
        self.fourmonth = thisTime - relativedelta(months=4)
        self.fivemonth = thisTime - relativedelta(months=5)
        self.sixmonth=thisTime - relativedelta(months=6)


    def getOneMonthly(self):
        for i in financeinfo.filter(USER_ID_id=self.thisPlayer).values():
            print(i['PAYMENTTIME'])
            sumforavg=0
            print(self.onemonth)
            if self.onemonth<i['PAYMENTTIME']<thisTime:
                sumforavg=sumforavg+i['PAYMENTPRICE']

        return round(sumforavg/3,0)





    def getTwoMonthly(self):
        for i in financeinfo.filter(USER_ID_id=self.thisPlayer).values():
            print(i['PAYMENTTIME'])
            sumforavg = 0
            print(self.onemonth)
            if self.twomonth < i['PAYMENTTIME'] < self.onemonth:
                sumforavg = sumforavg + i['PAYMENTPRICE']

        return round(sumforavg / 3, 0)

    def getThreeMonthly(self):

        for i in financeinfo.filter(USER_ID_id=self.thisPlayer).values():
            print(i['PAYMENTTIME'])
            sumforavg = 0
            print(self.onemonth)
            if self.threemonth < i['PAYMENTTIME'] < self.twomonth:
                sumforavg = sumforavg + i['PAYMENTPRICE']
        return round(sumforavg / 3, 0)


    def getFourMonthly(self):

        for i in financeinfo.filter(USER_ID_id=self.thisPlayer).values():
            print(i['PAYMENTTIME'])
            sumforavg = 0
            print(self.onemonth)
            if self.fourmonth < i['PAYMENTTIME'] < self.threemonth:
                sumforavg = sumforavg + i['PAYMENTPRICE']
        return round(sumforavg / 3, 0)



    def getFiveMonthly(self):

        for i in financeinfo.filter(USER_ID_id=self.thisPlayer).values():
            print(i['PAYMENTTIME'])
            sumforavg = 0
            print(self.onemonth)
            if self.fivemonth < i['PAYMENTTIME'] < self.fourmonth:
                sumforavg = sumforavg + i['PAYMENTPRICE']

        return round(sumforavg / 3, 0)



    def getSixMonthly(self):
        for i in financeinfo.filter(USER_ID_id=self.thisPlayer).values():
            print(i['PAYMENTTIME'])
            sumforavg = 0
            print(self.onemonth)
            if self.sixmonth < i['PAYMENTTIME'] < self.fivemonth:
                sumforavg = sumforavg + i['PAYMENTPRICE']
        return round(sumforavg / 3, 0)


from django.shortcuts import render
from mobet_app.models import User
from mobet_app.models import financeInfo
from mobet_app.models import participatedList
from mobet_app.models import competitionSet
from mobet_app.models import userGameRecord
from mobet_app.models import userRank


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



user = User.objects.all()
financeinfo=financeInfo.objects.all()
participatedlist=participatedList.objects.all()
competitionset=competitionSet.objects.all()
usergamerecord=userGameRecord.objects.all()
userrank = userRank.objects.all()
userrankdf=read_frame(userrank,fieldnames=['GRADE','WINRECORD','GAMECOUNT','POINTS','USER_ID_id'])

class UserInfo:
    
    def __init__(self,userid,grade,points,winrecord,gamecount):
        self.userid=userid
        self.grade=grade
        self.points=points
        self.winrecord=winrecord
        self.gamecount=gamecount

#given data







class PointVerdict:
    def __init__(self,thisPlayer,thisRoomNum):
        self.thisPlayer=thisPlayer
        self.thisRoomNum=thisRoomNum
        self.thisUserGrade = userrank.filter(USER_ID_id=thisPlayer).values()[0]['GRADE']
        self.thisUserWinRecord = userrank.filter(USER_ID_id=thisPlayer).values()[0]['WINRECORD']
        self.thisUserGameCount = userrank.filter(USER_ID_id=thisPlayer).values()[0]['GAMECOUNT']
        self.thisUserPoints = userrank.filter(USER_ID_id=thisPlayer).values()[0]['POINTS']

        self.thisplayerinfo = UserInfo(thisPlayer,self.thisUserWinRecord,self.thisUserGameCount, self.thisUserPoints,
                                    self.thisUserGrade)
        self.thisGameLeftMoney = \
            participatedlist.filter(ROOMNUM_ID_id=thisRoomNum).filter(USER_ID_id=thisPlayer).values(
                'LEFTMONEY')[0][
                'LEFTMONEY']
        self.thisRoomSetMoney = competitionset.filter(id=thisRoomNum).values('SETTINGMONEY')[0]['SETTINGMONEY']

        self.diffMoney = self.thisGameLeftMoney - self.thisRoomSetMoney



    def valFunc(self):

        compPlayerList = []
        compPlayerPointDic = dict()

        for i in participatedlist.filter(ROOMNUM_ID_id=self.thisRoomNum).values('USER_ID_id'):
            compPlayerList.append(i['USER_ID_id'])
            print(i)

        for i in compPlayerList:
            compPlayerPointDic[i] = userrank.filter(USER_ID_id=i).values('POINTS')

        thisStartDate = competitionset.filter(id=self.thisRoomNum).values('STARTDATE')[0]['STARTDATE']
        thisDueDate = competitionset.filter(id=self.thisRoomNum).values('DUEDATE')[0]['DUEDATE']

        dayDelta = (thisDueDate - thisStartDate).days

        # isSuccess = 0
        
        # 이거 쓰려면 해당방의 setmoney들고와야함
        tmpsum = 0
        for i in compPlayerPointDic:
            tmpsum = tmpsum + i

        difficulty = 10
        maxDate = 365
        maxweight = 300

        difficulty = difficulty + (dayDelta / maxDate * maxweight)
        difficulty = difficulty + (abs(self.diffMoney) / 10000)

        print(dayDelta)

        diffTool = difficulty / 10
        diffweight = 0

        if self.diffMoney < 0:
            diffTool = 10 - diffTool

            if diffTool == 1:
                diffweight = 1 / 2
            elif diffTool == 2:
                diffweight = 4 / 5
            elif diffTool == 3:
                diffweight = 6 / 5
            elif diffTool == 4:
                diffweight = 3 / 2
            elif diffTool == 5:
                diffweight = 2 / 1
            elif diffTool == 6:
                diffweight = 5 / 2
            elif diffTool == 7:
                diffweight = 14 / 5
            elif diffTool == 8:
                diffweight = 16 / 5
            elif diffTool == 9:
                diffweight = 19 / 5
            elif diffTool > 9:
                diffweight = 4 / 1

        else:
            diffTool = 0

        thisPlayerGrade = usergamerecord.filter(USER_ID_id=self.thisPlayer).values('GAMEGRADE')[0]['GAMEGRADE']

        if self.diffMoney > 0:
            rankWeight = math.log(self.diffMoney * (len(compPlayerList) - thisPlayerGrade + 1) + 1)
        else:
            rankWeight = math.log(abs(self.diffMoney) + 1) * (thisPlayerGrade / len(compPlayerList))

        valuedPoint = self.thisplayerinfo.points + (
                    abs((tmpsum / len(compPlayerList) - self.thisplayerinfo.points)) / 30) + (
                                    diffweight * rankWeight)

      
        return valuedPoint
       
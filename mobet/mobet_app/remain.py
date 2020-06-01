from django.shortcuts import render
from django.utils import timezone

import re
from mobet_app.models import User
from mobet_app.models import financeInfo
from mobet_app.models import participatedList
from mobet_app.models import categoryList
from mobet_app.models import competitionSet
from mobet_app.models import userRank

from collections import Counter
from mobet_app.models import userGameRecord
from collections import deque
import operator
from datetime import datetime
import datetime
from mobet_app.point import PointVerdict

from pandas import Series

from django.forms.models import model_to_dict

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django_pandas.io import read_frame
import pandas as pd



user = User.objects.all()
userrank = userRank.objects.all()
financeinfo = financeInfo.objects.all()
participatedlist = participatedList.objects.all()
competitionset = competitionSet.objects.all()
usergamerecord = userGameRecord.objects.all()
thisRoomPlayers=[]

# thisGameLeftMoney = \
# participatedlist.filter(ROOMNUM_ID_id=thisRoomNum).filter(USER_ID_id=thisPlayer).values('LEFTMONEY')[0][
#     'LEFTMONEY']
# thisRoomSetMoney = competitionset.filter(id=thisRoomNum).values('SETTINGMONEY')[0]['SETTINGMONEY']

# diffMon=thisGameLeftMoney - thisRoomSetMoney

# thisPlayerTimeLog = user.filter(id=thisPlayer).values('TIMELOG')[0]['TIMELOG']
# thisPlayerFinanceInfodf = financeinfo.filter(USER_ID_id=thisPlayer).to_dataframe()
# this = []
# for i in thisPlayerFinanceInfodf['PAYMENTTIME']:
#     if i > thisPlayerTimeLog:
#         this.append(thisPlayerFinanceInfodf[thisPlayerFinanceInfodf['PAYMENTTIME'] == i])

# thisPlayerFinanceInfoNewdf = pd.concat(this, ignore_index=False)


# for i in participatedlist.filter(ROOMNUM_ID=thisRoomNum).values('USER_ID'):
#     thisRoomPlayers.append(i['USER_ID'])

thisTime=timezone.now()

def f2(x):
    return x[1]

def Grading(thisPlayer,thisRoomNum,thisRoomPlayers):

    print('thisPlayer33:',thisPlayer)
    compPlayerdic=dict()
    for i in participatedlist.filter(ROOMNUM_ID=thisRoomNum).values('USER_ID'):
        thisRoomPlayers.append(i['USER_ID'])

    thisGameLeftMoney = \
    participatedlist.filter(ROOMNUM_ID_id=thisRoomNum).filter(USER_ID_id=thisPlayer).values('LEFTMONEY')[0][
        'LEFTMONEY']
    thisRoomSetMoney = competitionset.filter(id=thisRoomNum).values('SETTINGMONEY')[0]['SETTINGMONEY']

    diffMon=thisGameLeftMoney - thisRoomSetMoney


    for i in thisRoomPlayers:
        compPlayerdic[i] = participatedlist.filter(USER_ID_id=i).values('LEFTMONEY')[0]['LEFTMONEY']
        res=sorted(compPlayerdic.items(), key=f2)

    playerGradeDic = dict()
    success=0

    if diffMon>0:
        success=1



    for j in thisRoomPlayers:
        count = 0
        cnt = 0  # 나보다 점수 높은놈
        for i in res:
            if i[1] > participatedlist.filter(USER_ID_id=j).values('LEFTMONEY')[0]['LEFTMONEY']:
                cnt = cnt + 1

            elif i[1] == participatedlist.filter(USER_ID_id=j).values('LEFTMONEY')[0]['LEFTMONEY']:
                print(i)
                count = count + 1
        if count == len(thisRoomPlayers):
            playerGradeDic[j] = 1

        else:
            playergrade = count + cnt
            playerGradeDic[j] = playergrade

        # print("efef : ",success,thisTime,playerGradeDic[j],thisRoomNum,j,participatedlist.filter(ROOMNUM_ID=thisRoomNum).filter(USER_ID_id=j).
        #                         values("LEFTMONEY")[0]["LEFTMONEY"])
        # obj_id = competitionSet.objects.get(pk=thisRoomNum)
        # print("sivalrom : ", obj_id)
        check = userGameRecord.objects.filter(USER_ID_id=j, ROOMNUM_ID_id=thisRoomNum)
        print("check : ", check)
        if not check:
            newrecord=usergamerecord.create(SUCCESSES=success,RECORDDATE=thisTime,GAMEGRADE=playerGradeDic[j],
                                    ROOMNUM_ID_id=thisRoomNum,USER_ID_id=j,LEFTMONEY=
                                    participatedlist.filter(ROOMNUM_ID=thisRoomNum).filter(USER_ID_id=j).
                                    values("LEFTMONEY")[0]["LEFTMONEY"])
            getPoint=PointVerdict(j,thisRoomNum).valFunc()

            
            #print(userrank.filter(USER_ID=j).values('GAMECOUNT')[0]['GAMECOUNT'])
            rank_obj = userRank.objects.get(USER_ID=j)
            gamecount = rank_obj.GAMECOUNT + 1
            point = rank_obj.POINTS + getPoint
            winrecord = rank_obj.WINRECORD

            if success==1:
                winrecord = rank_obj.WINRECORD + 1
              
            updatRank=userRank.objects.get(USER_ID=j)
            updatRank.GAMECOUNT=gamecount
            updatRank.POINTS=point
            updatRank.WINRECORD=winrecord
            #updatRank.GRADE=GRADE
            updatRank.save()

                






        # 차례대로 방번호,카테고리리스트,마킹시간이후 가져온 데이터,받아온 데이터에서 소비금액을 카테고리별로 분류할 딕셔너리

class RemainMoneyCare:

    def __init__(self,thisPlayer,thisRoomNum):
        self.rmNumList=[]
        self.cgList=[]
        self.pureCGList=[]
        self.afterTimedf=[]
        self.thisPlayerCategorySet={}
        self.thisPlayerMoneyDic={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0,13:0}
        self.thisPlayer=thisPlayer
        self.setMoney={}
        self.thisRoomNum=thisRoomNum
        self.thisRoomPlayers=[]


        #self.thisPlayerFinanceInfodf=thisPlayerFinanceInfoNewdf

        self.thisPlayerFinanceListdf=participatedlist.filter(USER_ID_id=self.thisPlayer).values("ROOMNUM_ID")


        self.thisPlayerparticipatedListdf = participatedlist.filter(USER_ID_id=self.thisPlayer).values("ROOMNUM_ID")
        self.pureCGList=[]
        self.forAllSumList=[]
        self.delDupCateCode =[]
        self.dupCodeDic = dict()



    def extractRmNum(self):
        for i in range(len(self.thisPlayerparticipatedListdf)):
            self.rmNumList.append(self.thisPlayerparticipatedListdf[i]["ROOMNUM_ID"])


        return self.rmNumList


    def extractCGList(self):
        for i in range(len(self.rmNumList)):
            self.cgList.append(competitionset.filter(id=self.rmNumList[i]).values('CATEGORYCODE_id'))


        return self.cgList

    def extractPureCGList(self):
        print("thiplayer : ", self.thisPlayer)
        virtualDic = {}

        for i in range(len(self.rmNumList)):
            virtualDic[self.cgList[i][0]['CATEGORYCODE_id']] = self.rmNumList[i]
            self.pureCGList.append(self.cgList[i][0]['CATEGORYCODE_id'])

        return self.pureCGList

    #financeinfo을 날짜에 맞춰서 필터
    def ForthisPlayerMoneyDic(self):
        print('여기만 해결:',self.thisPlayer)
        thisPlayerTimeLog = user.filter(id=self.thisPlayer).values('TIMELOG')[0]['TIMELOG']
        thisPlayerFinanceInfodf = financeinfo.filter(USER_ID_id=self.thisPlayer).to_dataframe()
        this = []
        for i in thisPlayerFinanceInfodf['PAYMENTTIME']:
            if i > thisPlayerTimeLog:
                this.append(thisPlayerFinanceInfodf[thisPlayerFinanceInfodf['PAYMENTTIME'] == i])

        thisPlayerFinanceInfoNewdf = pd.concat(this, ignore_index=False)
        
        setMoney={}

        for i in self.pureCGList:
            for j in range(len(thisPlayerFinanceInfoNewdf)):
                tmp = re.findall("\d+",thisPlayerFinanceInfoNewdf.loc[j]['CATEGORYCODE'])
                tmp = int(tmp[0])
                if i == tmp:
                    tmmp = {i:thisPlayerFinanceInfoNewdf.loc[j]['PAYMENTPRICE']}
                    # thisPlayerCategorySet.add(tmp)
                    setMoney = Counter(setMoney) + Counter(tmmp)
                    self.thisPlayerMoneyDic.update(setMoney)
        return self.thisPlayerMoneyDic


    def forDelDupCateCode(self):
        self.delDupCateCode = list(set(self.pureCGList))

        return self.delDupCateCode

    def extractAllSumList(self):

        for j in self.delDupCateCode:
            if j == 13:
                forAllSum = 0
                for k in self.thisPlayerMoneyDic.values():
                    # print(thisPlayerMoneyDic.values())
                    forAllSum = forAllSum + k
                thisRoom = competitionset.filter(CATEGORYCODE=j).values('id')

                for p in thisRoom:
                    self.forAllSumList.append(participatedlist.filter(ROOMNUM_ID=p['id']).filter(USER_ID_id=self.thisPlayer).values(
                            "LEFTMONEY")[0]["LEFTMONEY"] - forAllSum)

        return self.forAllSumList

    def forDupCode(self):
        gb = list(set(self.pureCGList))
        for ip in gb:
            self.dupCodeDic[ip] = self.pureCGList.count(ip)

        return self.dupCodeDic

    def extractFinalValue(self):
        forDupSum=0
        forNorSum=0
        
        for i in self.dupCodeDic:
            # 중복 카테고리

            if self.dupCodeDic[i] > 1:
                forDupSum = forDupSum + self.thisPlayerMoneyDic[i]
                thisRoom = competitionset.filter(CATEGORYCODE=i).values('id')[0]['id']
                print("thisroom1 : ", thisRoom)
                # 아래 값을 DB에 갱신해주면
                this = \
                participatedlist.filter(ROOMNUM_ID=thisRoom).filter(USER_ID_id=self.thisPlayer).values("LEFTMONEY")[
                    0]["LEFTMONEY"] - forDupSum

                ##디비 수정
                updat=participatedList.objects.get(ROOMNUM_ID=thisRoom, USER_ID=self.thisPlayer)
                updat.LEFTMONEY = this
                updat.save()
                print("what : ", thisRoom,self.dupCodeDic[i],this)

                print(user.filter(id=self.thisPlayer).values("TIMELOG")[0])

                updateTime=User.objects.get(id=self.thisPlayer)
                updateTime.TIMELOG=thisTime
                updateTime.save()





            # 중복, all둘다아님
            else:
                
                forNorSum = forNorSum + self.thisPlayerMoneyDic[i]
                thisRoom = competitionset.filter(CATEGORYCODE=i).values('id')[0]['id']
                print(forNorSum)
                print("thisroom2 : ", thisRoom)
                # 아래값을 DB에 갱신해주면
                this = \
                participatedlist.filter(ROOMNUM_ID=thisRoom).filter(USER_ID_id=self.thisPlayer).values("LEFTMONEY")[
                    0]["LEFTMONEY"] - forNorSum
                print("this : ", this)
                ##디비 수정
                updat=participatedList.objects.get(ROOMNUM_ID=thisRoom, USER_ID=self.thisPlayer)
                updat.LEFTMONEY=this
                updat.save()

                #현 유저 timeLog에 저장

                updateTime=User.objects.get(id=self.thisPlayer)
                updateTime.TIMELOG=thisTime
                updateTime.save()


    def CheckTime(self):
        if competitionset.filter(id=self.thisRoomNum).values('DUEDATE')[0]['DUEDATE']<thisTime:
            checkFinish=competitionSet.objects.get(id=self.thisRoomNum)
            checkFinish.IS_FINISHED=1
            IS_FINISHED=1
            Grading(self.thisPlayer,self.thisRoomNum,self.thisRoomPlayers)
            checkFinish.save()



class Execute:
    def __init__(self, user_id, room_id):
        self.user_id = user_id
        self.room_id = room_id
        
        self.obj = RemainMoneyCare(user_id, room_id)

    def execute(self):
        self.obj.extractRmNum()
        self.obj.extractCGList()
        self.obj.extractPureCGList()
        self.obj.ForthisPlayerMoneyDic()
        self.obj.forDelDupCateCode()
        self.obj.extractAllSumList()
        self.obj.forDupCode()
        self.obj.extractFinalValue()
        self.obj.CheckTime()
        


    def loop(self):
        temp_list = self.obj.thisRoomPlayers
        for i in temp_list:
            if i==self.user_id:
                temp_list.remove(i)
                break
        print("sival2 : ", temp_list)
        print("sival3 : ", len(temp_list))
        for i in temp_list:
            print("sival4 : ", i)
            tmp=Execute(i,self.room_id)
            tmp.execute()



        print(timezone.now())



 
    
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
from mobet_app.point2 import PointVerdict
from mobet_app.Grading import Grading


import pandas as pd

user = User.objects.all()
userrank = userRank.objects.all()
financeinfo = financeInfo.objects.all()
participatedlist = participatedList.objects.all()
competitionset = competitionSet.objects.all()
usergamerecord = userGameRecord.objects.all()
thisRoomPlayers = []

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

thisTime = timezone.now()


def f2(x):
    return x[1]


def Grading(thisPlayer, thisRoomNum, thisRoomPlayers):

    compPlayerdic = dict()
    for i in participatedlist.filter(ROOMNUM_ID=thisRoomNum).values('USER_ID'):
        thisRoomPlayers.append(i['USER_ID'])

    thisGameLeftMoney = \
        participatedlist.filter(ROOMNUM_ID_id=thisRoomNum).filter(USER_ID_id=thisPlayer).values('LEFTMONEY')[0][
            'LEFTMONEY']
    thisRoomSetMoney = competitionset.filter(id=thisRoomNum).values('SETTINGMONEY')[0]['SETTINGMONEY']

    diffMon = thisGameLeftMoney - thisRoomSetMoney

    for i in thisRoomPlayers:
        compPlayerdic[i] = participatedlist.filter(USER_ID_id=i).values('LEFTMONEY')[0]['LEFTMONEY']
        res = sorted(compPlayerdic.items(), key=f2)

    playerGradeDic = dict()
    success = 0

    if diffMon > 0:
        success = 1
    print('디룸플',thisRoomPlayers)
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
        print('책흐',check)
        if not check:
            newrecord = usergamerecord.create(SUCCESSES=success, RECORDDATE=thisTime, GAMEGRADE=playerGradeDic[j],
                                              ROOMNUM_ID_id=thisRoomNum, USER_ID_id=j, LEFTMONEY=
                                              participatedlist.filter(ROOMNUM_ID=thisRoomNum).filter(USER_ID_id=j).
                                              values("LEFTMONEY")[0]["LEFTMONEY"])
            getPoint = PointVerdict(j, thisRoomNum).valFunc()

            # print(userrank.filter(USER_ID=j).values('GAMECOUNT')[0]['GAMECOUNT'])
            rank_obj = userRank.objects.get(USER_ID=j)
            gamecount = rank_obj.GAMECOUNT + 1
            point = rank_obj.POINTS + getPoint
            winrecord = rank_obj.WINRECORD
            forgd = Grading(thisPlayer)
            forgd.grading()

            if success == 1:
                winrecord = rank_obj.WINRECORD + 1

            updatRank = userRank.objects.get(USER_ID=j)
            updatRank.GAMECOUNT = gamecount
            updatRank.POINTS = point
            updatRank.WINRECORD = winrecord
            updatRank.GRADE=forgd.grading()
            updatRank.save()

        # 차례대로 방번호,카테고리리스트,마킹시간이후 가져온 데이터,받아온 데이터에서 소비금액을 카테고리별로 분류할 딕셔너리


class RemainMoneyCare:

    def __init__(self, thisPlayer, thisRoomNum):
        self.rmNumList = []
        self.cgList = []
        self.pureCGList = []
        self.afterTimedf = []
        self.thisPlayerCategorySet = {}
        self.thisPlayerMoneyDic = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
        self.thisPlayer = thisPlayer
        self.setMoney = {}
        self.thisRoomNum = thisRoomNum
        self.thisRoomPlayers = []
        self.notNewOne=0

        # self.thisPlayerFinanceInfodf=thisPlayerFinanceInfoNewdf

        self.thisPlayerFinanceListdf = participatedlist.filter(USER_ID_id=self.thisPlayer).values("ROOMNUM_ID")

        self.thisPlayerparticipatedListdf = participatedlist.filter(USER_ID_id=self.thisPlayer).values("ROOMNUM_ID")
        self.pureCGList = []
        self.forAllSum=0
        self.delDupCateCode = []
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

        virtualDic = {}

        for i in range(len(self.rmNumList)):
            virtualDic[self.cgList[i][0]['CATEGORYCODE_id']] = self.rmNumList[i]
            self.pureCGList.append(self.cgList[i][0]['CATEGORYCODE_id'])

        return self.pureCGList

    # financeinfo을 날짜에 맞춰서 필터
    def ForthisPlayerMoneyDic(self):
        print('ForthisPlayerROOMNUM',self.thisRoomNum)
        print('FORTHIPPLAYERTHIPLAYER',self.thisPlayer)
        thisPlayerTimeLog = participatedlist.filter(ROOMNUM_ID_id=self.thisRoomNum).filter(USER_ID_id=self.thisPlayer).values('TIMELOG')[0]['TIMELOG']
        thisPlayerFinanceInfodf = financeinfo.filter(USER_ID_id=self.thisPlayer).to_dataframe()
        this = []

        for i in thisPlayerFinanceInfodf['PAYMENTTIME']:
            #print(i)
            #print(thisPlayerTimeLog)
            if thisPlayerTimeLog == None or i > thisPlayerTimeLog:

                this.append(thisPlayerFinanceInfodf[thisPlayerFinanceInfodf['PAYMENTTIME'] == i])

        self.notNewOne=len(this)
       # print(self.notNewOne)

        if self.notNewOne!=0:
            thisPlayerFinanceInfoNewdf = pd.concat(this, ignore_index=False)
            setMoney = {}
           # print(thisPlayerFinanceInfoNewdf)

            for i in set(self.pureCGList):

                for j in range(len(thisPlayerFinanceInfoNewdf)):

                    print(thisPlayerFinanceInfoNewdf)
                    tmp = re.findall("\d+", thisPlayerFinanceInfoNewdf.iloc[j]['CATEGORYCODE'])

                    tmp = int(tmp[0])
                    if i == tmp:

                        tmmp = {i: thisPlayerFinanceInfoNewdf.iloc[j]['PAYMENTPRICE']}

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

                for k in self.thisPlayerMoneyDic.values():
                    # print(thisPlayerMoneyDic.values())

                    self.forAllSum = self.forAllSum + k


                print(self.forAllSum)
                thisRoom = competitionset.filter(CATEGORYCODE=j).values('id')

                # print(thisRoom[0])
                # # print('eltmfna',thisRoom)
                #
                #
                # for p in thisRoom:
                #     print(p)
                #
                #     updat = participatedList.objects.get(USER_ID=self.thisPlayer, ROOMNUM_ID=p['id'])
                #     print(p['id'],self.thisPlayer)
                #     updat.LEFTMONEY=participatedlist.filter(ROOMNUM_ID_id=p['id']).filter(USER_ID_id=self.thisPlayer).values(
                #         "LEFTMONEY")[0]["LEFTMONEY"] - forAllSum
                #     updat.save()
                    # updat.LEFTMONEY = allMoneyUpdat
                    # updat.save()




    def forDupCode(self):
        gb = list(set(self.pureCGList))
        for ip in gb:
            self.dupCodeDic[ip] = self.pureCGList.count(ip)

        return self.dupCodeDic

    def extractFinalValue(self):
        forSum = 0

        print('핵심',self.thisPlayer)

        this = 0

        # for i in self.dupCodeDic:

            # 중복 카테고리
        thisRoomCate = competitionset.filter(id=self.thisRoomNum).values('CATEGORYCODE')[0]['CATEGORYCODE']
        print('핵심2',thisRoomCate)

        if thisRoomCate==13:

            # fortheSum = fortheSum + self.thisPlayerMoneyDic[i]
            #
            #
            # print(fortheSum)

            # this = \
            #     participatedlist.filter(ROOMNUM_ID=thisRoom).filter(USER_ID_id=self.thisPlayer).values("LEFTMONEY")[
            #         0]["LEFTMONEY"] - fortheSum

            this= participatedlist.filter(ROOMNUM_ID=self.thisRoomNum).filter(USER_ID_id=self.thisPlayer).values("LEFTMONEY")[0]["LEFTMONEY"]-self.forAllSum
            print('i=13',this)
            updat = participatedList.objects.get(ROOMNUM_ID=self.thisRoomNum, USER_ID=self.thisPlayer)
            updat.LEFTMONEY = this
            updat.save()

            updateTime = participatedList.objects.get(USER_ID_id=self.thisPlayer,ROOMNUM_ID=self.thisRoomNum)
            updateTime.TIMELOG = thisTime
            updateTime.save()


        else:



            mb=self.thisPlayerMoneyDic[thisRoomCate]
            print(mb,'mb')
            # thisRoom = competitionset.filter(CATEGORYCODE=i).values('id')[0]['id']

            # 아래 값을 DB에 갱신해주면
            this = \
                participatedlist.filter(ROOMNUM_ID=self.thisRoomNum).filter(USER_ID_id=self.thisPlayer).values("LEFTMONEY")[
                    0]["LEFTMONEY"] - mb

            print('this:', this)

            print('thisplayer:', self.thisPlayer)

            ##디비 수정
            updat = participatedList.objects.get(ROOMNUM_ID=self.thisRoomNum, USER_ID=self.thisPlayer)
            updat.LEFTMONEY = this
            updat.save()

            updateTime = participatedList.objects.get(USER_ID=self.thisPlayer,ROOMNUM_ID=self.thisRoomNum)
            updateTime.TIMELOG = thisTime
            updateTime.save()




            #
            #
            # # 중복, all둘다아님
            # else:
            #
            #     print('n dup code',i)
            #     forNorSum = forNorSum + self.thisPlayerMoneyDic[i]
            #     thisRoom = competitionset.filter(CATEGORYCODE=i).values('id')[0]['id']
            #
            #     # 아래값을 DB에 갱신해주면
            #     this = \
            #         participatedlist.filter(ROOMNUM_ID=thisRoom).filter(USER_ID_id=self.thisPlayer).values("LEFTMONEY")[
            #             0]["LEFTMONEY"] - forNorSum
            #
            #     ##디비 수정
            #     updat = participatedList.objects.get(ROOMNUM_ID=thisRoom, USER_ID=self.thisPlayer)
            #     updat.LEFTMONEY = this
            #     print('neither this:',this)
            #     print('neither thisroom:', thisRoom)
            #     print('neither thisplayer:', self.thisPlayer)
            #     updat.save()
            #
            #     # 현 유저 timeLog에 저장
            #
            #     updateTime = participatedList.objects.get(id=self.thisPlayer)
            #     updateTime.TIMELOG = thisTime
            #     updateTime.save()

    def CheckTime(self):
        if competitionset.filter(id=self.thisRoomNum).values('DUEDATE')[0]['DUEDATE'] < thisTime:
            checkFinish = competitionSet.objects.get(id=self.thisRoomNum)
            checkFinish.IS_FINISHED = 1
            IS_FINISHED = 1
            Grading(self.thisPlayer, self.thisRoomNum, self.thisRoomPlayers)
            checkFinish.save()

    # def changeTimeLog(self):
    #     updateTime = participatedList.objects.get(id=self.thisPlayer)




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
        if self.obj.notNewOne!=0:
            self.obj.forDelDupCateCode()
            self.obj.extractAllSumList()
            self.obj.forDupCode()
            self.obj.extractFinalValue()

        self.obj.CheckTime()
        print('execute end')

    def loop(self):
        print('loop start')
        temp_list = self.obj.thisRoomPlayers
        for i in temp_list:
            if i == self.user_id:
                temp_list.remove(i)
                break


        for i in temp_list:
            print("thisRoomPlayer:",i)

            tmp = Execute(i, self.room_id)
            tmp.execute()
        print('loop END')







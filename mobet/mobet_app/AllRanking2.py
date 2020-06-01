from django.shortcuts import render
from mobet_app.models import User
from mobet_app.models import financeInfo
from mobet_app.models import participatedList
from mobet_app.models import competitionSet
from mobet_app.models import userGameRecord
from mobet_app.models import userRank
from django_pandas.io import read_frame
from django.utils import timezone



from collections import Counter
from collections import deque
import operator
from datetime import datetime
import datetime
import re
import math
from pandas import Series

import pandas as pd

from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response



class AllRanking:
    def __init__(self,thisPlayer):
        self.userrank = userRank.objects.all()
        self.userrankdf = read_frame(self.userrank, fieldnames=['GRADE', 'WINRECORD', 'GAMECOUNT', 'POINTS', 'USER_ID_id'])
        self.thisPlayer=thisPlayer
        self.sendDataDicFinal = {}


    def thisPlayerRank(self):
        pointSorted = sorted(self.userrankdf['POINTS'])
        gb = list(set(pointSorted))
        dupRankDic = dict()

        for ip in gb:
            dupRankDic[ip] = pointSorted.count(ip)

        pt = self.userrank.to_dataframe(fieldnames=('POINTS', 'GRADE', 'WINRECORD', 'GAMECOUNT', 'USER_ID'))
        forDupRankList = []
        for i, j in sorted(dupRankDic.items()):
            if j > 1:
                forDupRankList.append(i)
        rangeRankIndexList = []
        for i in reversed(forDupRankList):
            rangeRankIndexList.append(list(pt.loc[pt['POINTS'] == i].index))
            # print(pt.loc[pt['POINTS']==i].index)


        sendDataList = []



        for point in rangeRankIndexList:
            sendDataList.append(point[len(point) - 1] + 1)

        convertRangeRankIndexListToUserID = []
        for k in rangeRankIndexList:
            tmplst = []
            for j in range(len(k)):
                tmp = re.findall("\d+", pt.loc[k[j], 'USER_ID'])
                tmp = int(tmp[0])
                tmplst.append(tmp)
            convertRangeRankIndexListToUserID.append(tmplst)
        for i in range(len(convertRangeRankIndexListToUserID)):
            self.sendDataDicFinal[sendDataList[i]] = convertRangeRankIndexListToUserID[i]

        itFindWell = 0
        thisPlayerRanking = 0


        for i, j in self.sendDataDicFinal.items():
            if self.thisPlayer in j:
                thisPlayerRanking = i
                itFindWell = 1


        thisstr = 'User object ({0})'.format(self.thisPlayer)

        # 중복등수안에 있는게 아니라면,, 여길 들어간다
        if itFindWell == 0:
            thisPlayerRanking = pt[pt['USER_ID'] == thisstr].index[0]+1

        return thisPlayerRanking

    def AllRank(self):
        table=self.userrank.to_dataframe(fieldnames=('POINTS', 'GRADE', 'WINRECORD', 'GAMECOUNT', 'USER_ID'))
        arr=table.index.tolist()

        RankList=[]
        AllRankDic=dict()


        for i in arr:
            RankList.append(i+1)



        for j in range(len(RankList)):
            tmp = re.findall("\d+", table.loc[j, 'USER_ID'])
            tmp = int(tmp[0])
            AllRankDic[j+1]=tmp

        # print(AllRankDic)
        newDic=dict()
        if self.sendDataDicFinal == {}:
            return AllRankDic
        else:
            for k,p in self.sendDataDicFinal.items():
                for i,j in AllRankDic.items():
                    if j in p:
                        newDic[j]=k

                    else:
                        newDic[j]=i

            return newDic



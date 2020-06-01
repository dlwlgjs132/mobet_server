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



@api_view(['GET',])
def func(request):
    if request.method == 'GET':

        class AllRanking:
            def __init__(self):
                self.userrank = userRank.objects.all()
                self.userrankdf = read_frame(self.userrank, fieldnames=['GRADE', 'WINRECORD', 'GAMECOUNT', 'POINTS', 'USER_ID_id'])
            # 동점자처리,,

            # 점수가 같으면 rank순위를 중복으로,,,

            # points를 받아와서 이를 sort해주고 점수들이 같은것에 대해서 조정을 해주자

            def process(self):
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

            # print(rangeRankIndexList)
            # 각자 받은 값,, 공동 3등, 공동 8등 이런식,,,
            # 각 리스트에서 끝값+1을 하고 전달해주면 됨
            #

                sendDataList = []
                sendDataDicFinal = {}

            # print(sendDataDicFinal)
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
                    sendDataDicFinal[sendDataList[i]] = convertRangeRankIndexListToUserID[i]

            # 등수:해당 인덱스에 채워 넣으면됨 (인덱스가 0부터 시작이라 혹시,,보정이 필요할 수 있음)
            # print(sendDataDicFinal)
            # print(pt)

            # thisplayer==> dictionary(senddatadicfinal)value에 없으면
            # pk값을 그냥 받아와라

            #######순위 추출기능
                itFindWell = 0
                thisPlayerRanking = 0

            # 중복등수안에 있으면 여길 통과함
                for i, j in sendDataDicFinal.items():
                    if self.thisPlayer in j:
                        thisPlayerRanking = i
                        itFindWell = 1

                # 포밍해주기
                thisstr = 'User object ({0})'.format(self.thisPlayer)
                # 중복등수안에 있는게 아니라면,, 여길 들어간다
                if itFindWell == 0:
                    thisPlayerRanking = pt[pt['USER_ID'] == thisstr].index[0]

                arr=pt.index.tolist()
                RankList=[]
                AllRankDic=dict()
                for i in arr:
                   RankList.append(i+1)

                for j in range(len(RankList)):
                    tmp = re.findall("\d+", pt.loc[j, 'USER_ID'])
                    tmp = int(tmp[0])
                    AllRankDic[j+1]=tmp

                # print(pt)
                # print(AllRankDic)
                # thisTime = timezone.now()


            #
            # thisPlayerTimeLog=user.filter(id=thisPlayer).values('TIMELOG')[0]['TIMELOG']
            # print(financeinfo.filter(USER_ID_id=thisPlayer).values('PAYMENTTIME')[0]['PAYMENTTIME']>thisTime)
            # thisPlayerFinanceInfodf=financeinfo.filter(USER_ID_id=thisPlayer).to_dataframe()
            # #this=pd.DataFrame
            # this=[]
            # for i in thisPlayerFinanceInfodf['PAYMENTTIME']:
            #     if i<thisPlayerTimeLog:
            #         this.append(thisPlayerFinanceInfodf[thisPlayerFinanceInfodf['PAYMENTTIME']==i])
            #
            # newdf=pd.concat(this,ignore_index=False)
            # print(newdf)
            #










            #dictionary 두개를 돌아서 만약 첫번째 dic에 목록이 있으면 해당 내용을 교체하고 아니면 그냥 둬라



            # for i in range(len(pt)):

            # print(pt)

            #######

            # thisPlayer=2
            # for grade,player in sendDataDicFinal.items():
            #     if type(player)==list():
            #         if thisPlayer in player:
            #             print(grade)
            #         else:
            #             continue
            #     else:
            #         if thisPlayer==player:
            #             print(grade)
            #
            # print(pt)
            # print(sendDataDicFinal)

            # print(pt.loc[,]

            # print(len(pt))
            # 전체 플레이어수
            # 내 pt의 idx값
            # print(len(pt))

            # for i in pt:
            #     tmp=re.findall("\d+",i['USER_ID'])
            #     tmp=int(tmp[0])
            #     if tmp==thisPlayer:
            #

    return Response({"ok"})
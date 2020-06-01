from django.shortcuts import render
from django.utils import timezone

import re
from mobet_app.models import User
from mobet_app.models import userRank
# from mobet_app.models import RankTable

from collections import Counter

from collections import deque
import operator
from datetime import datetime
import datetime
from mobet_app.point2 import PointVerdict

user = User.objects.all()
userrank = userRank.objects.all()


class Grading:

    def __init__(self,thisPlayer):
        self.thisPlayer=thisPlayer


    def grading(self):
        obj_grade=userRank.objects.get(USER_ID=self.thisPlayer)
        thisUserPoint=obj_grade.POINTS


        if 1000<thisUserPoint<900:
            return 'A+'
        elif 850<=thisUserPoint<900:
            return 'A'

        elif 800<=thisUserPoint<850:
            return 'A-'

        elif 700<=thisUserPoint<800:
            return 'B+'

        elif 650<=thisUserPoint<700:
            return 'B'

        elif 600<=thisUserPoint<650:
            return 'B-'

        elif 500<=thisUserPoint<600:
            return 'C+'

        elif 300<=thisUserPoint<500:
            return 'C'

        elif 0<=thisUserPoint<300:
            return 'C-'



















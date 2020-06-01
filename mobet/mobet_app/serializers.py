from rest_framework import serializers
# models
from mobet_app.models import User
from mobet_app.models import categoryList
from mobet_app.models import competitionSet
from mobet_app.models import Notification
from mobet_app.models import participatedList
from mobet_app.models import Relationship
from mobet_app.models import financeInfo
from mobet_app.models import userRank

from django.forms.models import model_to_dict
import json
import datetime
 
# 사용자 정보
class MemberSerializer():
    id = 0
    nick = ''
    imgUrl = ''
    score = 0 # 점수
    grade = '' # 등급
    rank = 0 # 전체 등수
    remain = None # 게임 내 남은 금액
    place = None # 게임 내 등수place

    def __init__(self, id, nick, imgUrl, score=0, grade='', rank=0, remain=None, place=None):
        self.id = id
        self.nick = nick
        self.imgUrl = imgUrl
        self.score = score
        self.grade = grade
        self.rank = rank
        self.remain = remain
        self.place = place

# 사용자 정보를 저장하기 위한 것
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'USERID',
            'USERUID',
            'PHONENUM',
            'NICKNAME',
            'RECENTPAYAVG',
            'SIGNUPDATE',
            'PROFILEIMG'
        )   
# 참가자 정보
class participatedListSerializer(serializers.ModelSerializer):
    USER_ID = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='USERUID')

    # ROOMNUM_ID은 변수명 같이해서 받은다음에 pk로 자동저장
    # LEFTMONEY는 처음에 settingmoney와 동일하게
    class Meta:
        model = participatedList
        fields = (
            'pk',
            'USER_ID',
            'ROOMNUM_ID',
            'TIMELOG'
            'LEFTMONEY'
        )

def f2(x):
    return x[1]
# 방생성
class CompetitionSetSerializer(serializers.ModelSerializer):
    # CATEGORYCODE = serializers.SlugRelatedField(queryset=categoryList.objects.all(), slug_field='CATEGORY')
    OWNER_ID = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='USERUID')
# 방장여부, 참가 여부, 게임시작 여부, 방장 정보(점수, 등급, 전체순위, 남은 금액, 등수), 참가자 정보(리스트)
    is_admin = serializers.SerializerMethodField()
    compete = serializers.SerializerMethodField()
    is_start = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    owner_profile = serializers.SerializerMethodField()
    # members = serializers.SerializerMethodField()
    def get_is_admin(self, obj):
        return False
    def get_compete(self, obj):
        return False
    def get_is_start(self, obj):
        if obj.STARTDATE < datetime.datetime.now():
            return True
        return False
    def get_owner_profile(self, obj):
        member = MemberSerializer(obj.OWNER_ID.id, obj.OWNER_ID.NICKNAME,obj.OWNER_ID.PROFILEIMG)
        return member.__dict__

    def get_members(self, obj):
        # 방에 참가중인 멤버들 가져오기
        member_list = list()
        participate_memebers = participatedList.objects.filter(ROOMNUM_ID=obj.pk)

        sort_dict = dict()

        for p in participate_memebers:
            p_dict = model_to_dict(p)
            user_id = p_dict['USER_ID']  
            user = User.objects.filter(pk=user_id)
            # 등수 추가해야함
            user = user.values()[0]
            ####################
            # rank는 전체등수
            user_rank = userRank.objects.get(USER_ID=user_id)
            score = user_rank.POINTS
            grade = user_rank.GRADE
            # grade = USERRANK GRADE
            # place = participatedlist에서 계산해서 보내야함
            left_money = p_dict['LEFTMONEY']
            sort_dict[user_id] = left_money
            member = MemberSerializer(user['id'], user['NICKNAME']
            ,user['PROFILEIMG'], score=score, grade=grade, rank=0, remain=left_money, place=None)
            member_list.append(member.__dict__)

        # res는 튜플의 리스트
        res = sorted(sort_dict.items(), key=f2)

        for idx, m in enumerate(member_list):
            index, value = res[idx]
            m['place'] = idx + 1

        return member_list
    
    class Meta:
        model = competitionSet
        fields = (
                'pk',
                'ROOMNAME',
                'OWNER_ID',
                'STARTDATE',
                'DUEDATE',
                'CATEGORYCODE',
                'SETTINGMONEY',
                'RECENTPAYAVGMIN',
                'RECENTPAYAVGMAX',
                'OPEN',
                'is_admin',
                'compete',
                'is_start',
                'owner_profile',
                'members'
                )

# 카테고리 추가(카테고리는 디비에 저장해놓지만 테스트용으로 만듬)
class GameCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = categoryList
        fields=(
            'pk',
            'CATEGORY'
        )

# 친구추가(아직은 뷰에 추가되진 않았지만 후에 추가될 것을 대비, 테스트)
class RelationshipSerializer(serializers.ModelSerializer):
    # USERONE, USERTWO는 pk값으로 받아야한다.
    # 친구의 MemberSerializer를 보내야한다.(목록 보낼 때)
    friend_inform = serializers.SerializerMethodField()

    def get_friend_inform(self, obj):
        member = MemberSerializer(obj.USERTWO.id, obj.USERTWO.NICKNAME,obj.USERTWO.PROFILEIMG)
        return member.__dict__

    class Meta:
        model = Relationship
        fields = (
            'pk',
            'USERONE',
            'USERTWO',
            'friend_inform',
        )
# 친구목록에서 게임 초대요청, 알림확인
class NotificationSerializer(serializers.ModelSerializer):
    OWNER_ID = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='USERUID')
    # notification = "efe"
    owner_profile = serializers.SerializerMethodField()
    game_name = serializers.SerializerMethodField()

    # FK로 관계되어있는 pk에 관한 정보가 담겨있다.
    def get_owner_profile(self, obj):
        # user_profile = obj.OWNER_ID
        member = MemberSerializer(obj.OWNER_ID.id, obj.OWNER_ID.NICKNAME,obj.OWNER_ID.PROFILEIMG)
        return member.__dict__

    def get_game_name(self, obj):
        room_name = obj.ROOMNAME.ROOMNAME
        return room_name

    class Meta:
        model = Notification
        fields = (
            'pk',
            'OWNER_ID',
            'ROOMNAME',
            'game_name',
            'USER_ID',
            'owner_profile'
        )

class financeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = financeInfo
        fields = (
            'pk',
            'USER_ID',
            'CATEGORYCODE',
            'STORE',
            'PAYMENTPRICE',
            'PAYMENTTIME'
        )

class userRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = userRank
        fields = (
            'pk',
            'USER_ID',
            'GRADE',
            'POINTS',
            'WINRECORD',
            'GAMECOUNT'
        )


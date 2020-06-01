# others
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import requests
import time
import os

# models
from mobet_app.models import User
from mobet_app.models import competitionSet
from mobet_app.models import Notification
from mobet_app.models import participatedList
from mobet_app.models import Relationship
from mobet_app.models import categoryList
from mobet_app.models import Image
from mobet_app.models import financeInfo
from mobet_app.models import userRank

# serializers
from mobet_app.serializers import UserSerializer
from mobet_app.serializers import CompetitionSetSerializer
from mobet_app.serializers import GameCategorySerializer
from mobet_app.serializers import NotificationSerializer
from mobet_app.serializers import participatedListSerializer
from mobet_app.serializers import RelationshipSerializer
from mobet_app.serializers import MemberSerializer
from mobet_app.serializers import financeInfoSerializer
from mobet_app.serializers import userRankSerializer

from django.forms.models import model_to_dict
from datetime import datetime, timedelta
from mobet_app.test import test2
from mobet_app.remain2 import Execute
from mobet_app.AllRanking2 import AllRanking
from mobet_app.monthly import Monthly

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
CONFIG_SECRET_DIR = os.path.join(ROOT_DIR, '.config_secret')
CONFIG_SETTINGS_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, 'settings_common.json')
DEFAULT_IMG = os.path.join(ROOT_DIR, 'profile.jpg')

config_secret = json.loads(open(CONFIG_SETTINGS_COMMON_FILE).read())

def get_category_code(category):
    category_code = 0
    # 영화, 디저트
    if category == '음식점':
        category_code = 1
    elif category == '카페':
        category_code = 2
    elif category == '어린이집, 유치원':
        category_code = 4
    elif category == '학원':
        category_code = 4
    elif category == '문화시설':
        category_code = 5
    elif category == '대형마트':
        category_code = 6
    elif category == '병원':
        category_code = 7
    elif category == '약국':
        category_code = 7
    elif category == '주차장':
        category_code = 9
    elif category == '편의점':
        category_code = 10  
    elif category == '숙박':
        category_code = 11
    elif category == '주유소, 충전소':
        category_code = 12
    else : 
        category_code = 13

    return category_code

@api_view(['POST'])
def delete_user(request):
    if request.method == 'POST':
        data =  json.loads(request.body)
        obj = User.objects.get(pk=data['id'])

        obj.delete()
        return Response({"code":0})
# 닉네임 중복확인
@api_view(['POST',])
def nickname_check(request):
    if request.method == 'POST':
        # NICKNAME = request.POST.get('NICKNAME')
        NICKNAME = json.loads(request.body)
        try:# 닉네임 이미 존재 => 실패
            nickname = User.objects.get(NICKNAME=NICKNAME)
            # print(nickname)
            return Response({"code":1})
        except:# 닉네임 없는 경우 => 성공
            return Response({"code":0})

# 이메일 확인
@api_view(['POST',])
def userid_check(request):
    if request.method == 'POST':
        # USERID = request.POST.get('USERID')
        # USERID = request.data
        USERID = json.loads(request.body)
        # print(list(USERID.keys())[0])
        try: # 아이디 이미 존재 => 실패
            userid = User.objects.get(USERID=USERID)
            return Response({"code":1})
        except: # 아이디 중복 x => 성공
            return Response({"code":0})

# 핸드폰 번호 확인
@api_view(['POST',])
def phonenum_check(request):
    if request.method == 'POST':
        # USERID = request.POST.get('USERID')
        # USERID = request.data
        PHONENUM = json.loads(request.body)
        # print(list(USERID.keys())[0])
        try: # 아이디 이미 존재 => 실패
            phone_number = User.objects.get(PHONENUM=PHONENUM)
            print("phone number : ", phone_number)
            # filter(PHONENUM=PHONENUN)으로 테스트
            return Response({"code":1})
        except: # 아이디 중복 x => 성공
            return Response({"code":0})

# 회원가입 요청
@api_view(['GET', 'POST'])
def sign_up(request):
    if request.method == 'GET':
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        # 기본 이미지 저장
        data['PROFILEIMG'] = DEFAULT_IMG
        user_serializer = UserSerializer(data=data)
        # print(user_serializer)
        if user_serializer.is_valid():
            obj = user_serializer.save()

            send_data = dict()
            # 바꿔야함
            # send_data['user_name'] = '이하른'
            send_data['user_phoneID'] = user_serializer.data['USERUID']
            send_data['user_phoneNum'] = user_serializer.data['PHONENUM']
            
            # 샌드박스 팀에 회원정보 보내기
            # !! 유의사항 : 샌드박스 팀에 디비에 있는 phonenum을 보내야한다.
            url = config_secret['sign_up_url']
            response = requests.post(url, json=send_data)
            print(response.json())
            if response.json() == 0:
                # 샌드박스팀에 정보 요청
                N = 180
                start_date = datetime.now() - timedelta(days=N)
                today = datetime.now()

                send_data = dict()
                send_data['user_phoneID'] = user_serializer.data['USERUID']
                send_data['bank_deposit'] = "출금"
                send_data['start_date'] = "{}-{}-{}".format(start_date.year,start_date.month, start_date.day)
                send_data['end_date'] = "{}-{}-{}".format(today.year, today.month, today.day+1)

                url = config_secret['finance_info_url']
                response = requests.post(url, json=send_data)
                # 거래내역 리스트 

                data = response.json()
                print(data)
                if response.status_code == 200:
                    for d in data:
                        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
                        # value 부분에 받은 데이터의 가게이름 넣기
                        params = {'query': d['bank_store']}
                        # 카카오 key 숨겨야한다.
                        headers = {'Authorization': config_secret['kakao_authorization']}
                        response = requests.get(url, params=params, headers=headers)
                        
                        response_data = response.json()['documents']

                        if response_data == []: 
                            category_code = 13
                        else:
                            category_name = response_data[0]['category_group_name']
                            category_code = get_category_code(category_name)

                        store_data = dict()
                        store_data['USER_ID'] = user_serializer.data['pk']
                        store_data['CATEGORYCODE'] = category_code
                        store_data['STORE'] = d['bank_store']
                        store_data['PAYMENTPRICE'] = d['bank_amount']
                        store_data['PAYMENTTIME'] = d['bank_date']
                        financeinfo_serializer = financeInfoSerializer(data=store_data)

                        if financeinfo_serializer.is_valid():
                            financeinfo_serializer.save()
                            print(financeinfo_serializer.data)
                        else:
                            return Response({"code":1})
                        
                    # userRank 생성하기
                    rank_data = {"USER_ID":user_serializer.data['pk']}
                    user_rank_serializer = userRankSerializer(data=rank_data)

                    if user_rank_serializer.is_valid():
                        user_rank_serializer.save()
                    else:
                        return Response({"code":1})
                # 받은 6개월치 데이터를 분류하고 디비에 저장하기
                # 리스트로 받으면 돌면서 financeInfo 디비에 저장한다.
                    print("good youre success")
                    return Response({"code":0})
                else: 
                    obj.delete()
                    print("fail")
                    return Response({"code":1})
            else : 
                obj.delete()
                return Response({"code":1})
        else :
            return Response({"code":1})
# 로그인 할 때 pk값 넣어서 보내기
@api_view(['GET',])
def login(request):
    if request.method == 'GET':
        user_uid = request.META['HTTP_AUTHORIZATION']
        try:
            user = User.objects.filter(USERUID=user_uid).values('id')
            user_id = user[0]['id']

            return Response({"code":user_id})
        except:
            return Response({"code":0})
# 게임 생성 및 모든 게임 조회
@api_view(['GET','POST'])
def game(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # request.META['HTTP_AUTHORIZATION'] => header의 authorization 확인
        data['OWNER_ID'] = request.META['HTTP_AUTHORIZATION']
        # data = json.loads(request.body)
        # data['USER_ID'] = request.META['HTTP_AUTHORIZATION']

        competitionset_serializer = CompetitionSetSerializer(data=data)

        if competitionset_serializer.is_valid():
            obj = competitionset_serializer.save()
            # print(competitionset_serializer.data)

            participate_dict = dict()
            participate_dict['USER_ID'] = data['OWNER_ID']
            participate_dict['ROOMNUM_ID'] = obj.id
            participate_dict['LEFTMONEY'] = data['SETTINGMONEY']
            participate_dict['TIMELOG'] = datetime.now()

            participated_serializer = participatedListSerializer(data=participate_dict)

            if participated_serializer.is_valid():
                participated_serializer.save()
                # print(participated_serializer.data)
            else : 
                obj.delete()
                return Response({"code":1})

            return Response({"code":0})
        
        return Response({"code":1})
    # 모든 게임 조회
    elif request.method == 'GET':
        games = competitionSet.objects.all()
        competitionset_serializer = CompetitionSetSerializer(games, many=True)
        
        temp_serializer = list()

        for c in competitionset_serializer.data:
            if c['is_start'] is False:
                temp_serializer.append(c)
        
        return Response(temp_serializer)

# 1개의 방정보 체크
@api_view(['POST'])
def game_inform(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        game = competitionSet.objects.get(pk=data['id'])
        
        game_serializer = CompetitionSetSerializer(game)

        user_uid = request.META['HTTP_AUTHORIZATION']
        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        # serializer는 immutable하다
        # 방장이면
        temp_data = dict()
        temp_data.update(game_serializer.data)

        if user_uid == game_serializer.data['OWNER_ID']:
            temp_data['is_admin'] = True
        
        # 참가 여부
        # roomnum 이랑 id 해서 있으면 True, 
        for member in game_serializer.data['members']:
            if member['id'] == user_id:
                temp_data['compete'] = True
                break

        return Response(temp_data)

# 카테고리 저장
@api_view(['POST',])
def category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category_serializer = GameCategorySerializer(data=data)
        
        if category_serializer.is_valid():
            category_serializer.save()

            return Response({"code":0})
        
        return Response({"code":1})

# 알림 저장
@api_view(['GET', 'POST'])
def notify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # OWNER_ID는 헤더값으로 받고
        # ROOMNAME_ID를 code로 받음
        # USER_ID는 id로 받음
        owner_uid = request.META['HTTP_AUTHORIZATION']
        for d in data:
            temp_data = dict()
            temp_data['OWNER_ID'] = owner_uid
            temp_data['ROOMNAME'] = d['code']
            temp_data['USER_ID'] = d['id']
            
        # 리스트로 바꾸기
            notification_serializer = NotificationSerializer(data=temp_data)
            print(notification_serializer) 

            if notification_serializer.is_valid():
                notification_serializer.save()

            else: return Response({"code":1})

        return Response({"code":0})
    # 알림 다 보내기
    elif request.method == 'GET':
        # 나의 alram -> true로 바꾸기
        user_uid = request.META['HTTP_AUTHORIZATION']
        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']
        # true로 바꾸기
        noti = Notification.objects.filter(USER_ID=user_id).update(ALARM=True)
        # User.objects.all().update(PROFILEIMG="https://ljm.wo.tc/test/profile.jpg")

        notifies = Notification.objects.filter(USER_ID=user_id)

        # owner 프로필, 방 pk, 이름 추가
        notification_serializer = NotificationSerializer(notifies, many=True)
        print(notification_serializer)
        return Response(notification_serializer.data)
# 메인 화면에서 알림이 있는지 없는지 확인
@api_view(['GET','POST'])
def notify_check(request):
    if request.method == 'POST':
        # client에서 보낸 UID 값의 alarm false가 있는지 확인
        data = request.META['HTTP_AUTHORIZATION']
        print("data:",data)
        user = User.objects.filter(USERUID=data).values('id')
        user_id = user[0]['id']

        noti = Notification.objects.filter(USER_ID=user_id).values('ALARM')
        
        # false가 있는지 확인
        if not noti: # 없을경우
            return Response({"code":0})
        else: # 있는경우
            # false가 있는지 확인
            if noti.filter(ALARM=False).exists():
                return Response({"code":1})
            else:
                return Response({"code":0})
        
# 수락, 거절 버튼 눌렀을 때
@api_view(['POST',])
def delete_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # notification의 id를 받으면 해당 id 삭제
        try:
            notification = Notification.objects.get(id=data['id'])
            # 친구 수락, 거절은 따로 데이터 추가해야함
            # 친구 수락할 경우 데이터를 추가해야해서
            notification.delete()

            return Response({"code":0})

        except:
            return Response({"code":1})

# 방참가 요청
@api_view(['POST'])
def participate_game(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['USER_ID'] = request.META['HTTP_AUTHORIZATION']

        user = User.objects.filter(USERUID=data['USER_ID']).values('id')
        user_id = user[0]['id']

        participated_check = participatedList.objects.filter(ROOMNUM_ID=data['ROOMNUM_ID'], USER_ID=user_id)

        if not participated_check:# 없을 경우
            left_money = competitionSet.objects.get(pk=data['ROOMNUM_ID'])
            left_money = model_to_dict(left_money)['SETTINGMONEY']

            data['LEFTMONEY'] = left_money
            data['TIMELOG'] = datetime.now()
            # left_money = left_money[0]['id']
            # 남은금액은 참가한 방의 setting money로 
            # data['LEFTMONEY'] = left_money
            participated_serializer = participatedListSerializer(data=data)

            if participated_serializer.is_valid():
                participated_serializer.save()

                return Response({"code":0})

        return Response({"code":1})

# 방장이 게임 지우기
@api_view(['POST'])
def delete_game(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_uid = request.META['HTTP_AUTHORIZATION']
    

        game = competitionSet.objects.get(pk=data['id'])
        owner_id = game.OWNER_ID.id

        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']
        print(user_id, owner_id)
        if not game: # 없는 경우
            return Response({"code":1})
        else :
            if owner_id == user_id:
                game.delete()

                return Response({"code":0})
            else :
                return Response({"code":1})
# 친구목록 불러오기
@api_view(['GET','POST'])
def friend_list(request):
    # 내 UID를 통해서 친구목록 보내기
    if request.method == 'GET':
        user_uid = request.META['HTTP_AUTHORIZATION']
        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        friend_list = list()
        friends = Relationship.objects.filter(USERONE=user_id)
        for friend in friends:
            # f = model_to_dict(friend)
            print(friend.USERTWO.id, friend.USERTWO.NICKNAME, friend.USERTWO.PROFILEIMG)
            m = MemberSerializer(friend.USERTWO.id, friend.USERTWO.NICKNAME, friend.USERTWO.PROFILEIMG)
            friend_list.append(m.__dict__)

        # friend_serializer = RelationshipSerializer(friend, many=True)
        return Response(friend_list)
        # 데이터 받고 반환 안해도 되는지 competitionset에서 확인해보기
    # 친구 추가
    # 나중에 알림 메세지를 먼저 보내서 수락하면 추가하는 방식으로 바꿔야함
    # UID, 친구 pk를 통해서 추가
    elif request.method == 'POST':
        data = json.loads(request.body)
        user_uid = request.META['HTTP_AUTHORIZATION']

        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        data_dict = dict()
        data_dict['USERONE'] = user_id
        
        user2 = User.objects.filter(NICKNAME=data).values('id')

        if not user2:
            return Response({"code":1})
        
        data_dict['USERTWO'] = user2[0]['id']
        
        relationship_serializer = RelationshipSerializer(data=data_dict)
        print(relationship_serializer)
        if relationship_serializer.is_valid():
            relationship_serializer.save()

            return Response({"code":0})

        return Response({"code":1})

# 친구 삭제
@api_view(['POST'])
def friend_delete(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_uid = request.META['HTTP_AUTHORIZATION']

        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        
        friend = Relationship.objects.filter(USERONE=user_id, USERTWO=data['id'])
        if not friend:
            return Response({"code":1})
        else:
            friend.delete()
            return Response({"code":0})
# 방 나가기
@api_view(['POST'])
def game_exit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_uid = request.META['HTTP_AUTHORIZATION']

        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        obj = participatedList.objects.filter(ROOMNUM_ID=data['ROOMNUM_ID'], USER_ID=user_id)
        
        if not obj:# 없는경우(잘못된 요청)
            return Response({"code":1})
        else:
            obj.delete()
            return Response({"code":0})


# 샌드박스팀에서 정보받기
# 이 부분은 클라이언트에서 요청하는 것이 아니다.
@api_view(['POST'])
def finance_inform(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        
        user_uid = data['user_phoneID']
        user = User.objects.filter(USERUID=user_uid)

        if not user: # 회원정보가 없으면
            return Response({"code":1})
        else : # 회원 정보가 들어오면
            # 받은 정보를 financeinfo에 저장하고
            # 카카오 API 불러와서 카테고리 분류
            # 카테고리가 없으면 전체로 저장
            if data['bank_deposit'] != "출금": return Response({"code":0})
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            # value 부분에 받은 데이터의 가게이름 넣기
            params = {'query': data['bank_store']}
            headers = {'Authorization': config_secret['kakao_authorization']}

            response = requests.get(url, params=params, headers=headers)

            response_data = response.json()['documents']
            if response_data == []: 
                category_code = 13
            else:
                category_name = response_data[0]['category_group_name']
                category_code = get_category_code(category_name)
            
            print(category_code)
            user = user.values('id')
            user_id = user[0]['id']

            temp_data = dict()
            temp_data['USER_ID'] = user_id
            temp_data['CATEGORYCODE'] = category_code
            temp_data['STORE'] = data['bank_store']
            temp_data['PAYMENTPRICE'] = data['bank_amount']
            temp_data['PAYMENTTIME'] = data['bank_date']
            # 있는 회원이면 넣기
            # 있으면 serializer
            financeinfo_serializer = financeInfoSerializer(data=temp_data)
            print(temp_data)

            if financeinfo_serializer.is_valid():
                # 저장
                financeinfo_serializer.save()
                # 형이 짠 코드 불러오기
                return Response({"code":0})
            else :
                return Response({"code":1})

# 프로필 이미지 저장
@api_view(['POST'])
def restore_img(request):
    if request.method == 'POST':
        image = request.FILES.get('upload')
        user_uid = request.META['HTTP_AUTHORIZATION']
        print(user_uid)
        
        try:
            user = User.objects.filter(USERUID=user_uid).values('id')
            user_id = user[0]['id']
            print(user_id)

            millis = int(round(time.time() * 1000))
            image.name = str(millis) + image.name 
            obj = Image.objects.create(image=image)
            # 이미지 주소 반환 하기
            img_url = config_secret['s3_url'] + image.name
            print(img_url)
            # 해당 pk에 맞는 것을 저장
            user_obj = User.objects.filter(pk=user_id)
            user_obj.update(PROFILEIMG=img_url)
    
            return Response({"code":0})
        except :
            return Response({"code":1})
    

# 마이페이지 정보 요청(본인이 참가했던 전체)
@api_view(['GET'])
def mypage(request):
    if request.method == 'GET':
        user_uid = request.META['HTTP_AUTHORIZATION']

        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        
        # 진행중인거 종료된거 나눠야한다.
        # 진행중
        playing = list()
        # 끝난 것
        ending = list()

        participated_list = participatedList.objects.filter(USER_ID=user_id).values('ROOMNUM_ID')
        
        data = dict()
        
        if not participated_list:# 참가한 방이 없을 경우
            data['playing'] = playing
            data['ending'] = ending
        else:
            for idx, p in enumerate(participated_list):
                print(type(p))
                roomnum_id = p['ROOMNUM_ID']
                competition = competitionSet.objects.get(pk=roomnum_id)
                competitionset_serializer = CompetitionSetSerializer(competition)

                if competition.STARTDATE < datetime.now():
                    execute = Execute(user_id,roomnum_id)
                    execute.execute()
                    execute.loop()
                # 끝났으면
                if competition.DUEDATE < datetime.now():
                    ending.append(competitionset_serializer.data)
                else: # 진행중이면 
                    playing.append(competitionset_serializer.data)

            data['playing'] = playing
            data['ending'] = ending
        # user 정보 담는거
        user = User.objects.get(pk=user_id)

        user_rank = userRank.objects.get(USER_ID=user_id)
        score = user_rank.POINTS
        grade = user_rank.GRADE
        
        left_money = 0
        member = MemberSerializer(user.id, user.NICKNAME
        ,user.PROFILEIMG, score=score, grade=grade, rank=0, remain=left_money, place=None)

        data['my'] = member.__dict__

        return Response(data)

# 마이페이지에서 방 정보요청
@api_view(['GET'])
def mypage_into_room(request):
    if request.method == 'GET':
        # 공개방에서 들어갈 때랑 거의 같게 
        # Execute(user_id, room_id)
        # execute = Execute(1,1)
        # execute.execute()
        # execute.loop()

        return Response({"code":0})

# 가계부 정보 요청
@api_view(['GET'])
def account_inform(request):
    if request.method == 'GET':
        user_uid = request.META['HTTP_AUTHORIZATION']

        user = User.objects.filter(USERUID=user_uid).values('id')
        user_id = user[0]['id']

        # history : [{거래내역, 카테고리, 금액, 날짜}]
        account_dict = dict()
        history_items = list()
        account_obj = financeInfo.objects.filter(USER_ID=user_id)
        if not account_obj:
            history_items = list()
        else :
            account_serializer = financeInfoSerializer(account_obj, many=True)
            
            for account in account_serializer.data:
                temp_dict = dict()
                temp_dict['name'] = account['STORE']
                temp_dict['category'] = account['CATEGORYCODE']
                temp_dict['money'] = account['PAYMENTPRICE']
                temp_dict['date'] = account['PAYMENTTIME']

                history_items.append(temp_dict)

        # month : [{월, 월 지출 총합}]
        # yyyy-mm-01
        month_items = list()
        get_month_money = Monthly(user_id)

        temp_money = get_month_money.getFiveMonthly()
        temp_month = "2020-01-01"
        month = 1
        for m in range(0,4):
            month_dict = dict()
            month_dict['month'] = temp_month 
            month_dict['sum'] = temp_money

            if m == 0:
                temp_money = get_month_money.getFourMonthly()
            elif m == 1:
                temp_money = get_month_money.getThreeMonthly()
            elif m == 2:
                temp_money = get_month_money.getTwoMonthly()
            elif m == 3:
                temp_money = get_month_money.getOneMonthly()
            elif m == 4:
                temp_money = get_month_money.getOneMonthly()

            month = month + 1
            temp_month = "2020-0{}-01".format(month)
            month_items.append(month_dict)

        data = dict()
        data['history'] = history_items
        data['month'] = month_items

        return Response(data)
        
# 본인 ranking data
# input id
# return rankItem(first(1등비율), wins(승리횟수), paytimes(경쟁전수), toppercent(상위 몇퍼),nextrank(다음 등급가지남은거))
@api_view(['POST'])
def my_ranking(request):
    if request.method == 'POST':
        user = MemberSerializer(id=1, nick="AYA DODO AYA", 
        imgUrl=DEFAULT_IMG, score=700, grade='B+', rank=7, remain=None, place=None)

        rank_dict = dict()
        rank_dict['my'] = user.__dict__
        rank_dict['nextRank'] = 30
        rank_dict['toppercent'] = 24
        rank_dict['wins'] = 15
        rank_dict['first'] = 10
        rank_dict['playtimes'] = 58
        
        # allRanking= AllRanking(1)
        # allRanking.thisPlayerRank()
        # allRanking.AllRank()


        # allRanking2= AllRanking(3)
        # #인자는 유저 아이디


        return Response(rank_dict)

# 전체 랭킹
# return List<UserItem>
# @api_view(['GET'])
# def rank_list(request):
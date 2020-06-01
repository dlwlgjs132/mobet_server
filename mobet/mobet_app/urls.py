from django.conf.urls import url
from mobet_app import views

urlpatterns = [
    url(r'^sign-up/$', views.sign_up),
    url(r'^login/$', views.login),
    url(r'^nickname-check/$', views.nickname_check),
    url(r'^userid-check/$', views.userid_check),
    url(r'^phonenum-check/$', views.phonenum_check),
    url(r'^what-test/$', views.what_test),
    url(r'^game/$', views.game),
    url(r'^category/$', views.category),
    url(r'^notification/$',views.notify),
    url(r'^delete-alarm/$', views.delete_notification),
    url(r'^alarm-check/$', views.notify_check),
    url(r'^participate/$', views.participate_game),
    url(r'^friend-list/$', views.friend_list),
    url(r'^game-inform/$', views.game_inform),
    url(r'^game-exit/$', views.game_exit),
    url(r'^game-delete/$', views.delete_game),
    url(r'^finance-inform/$', views.finance_inform),
    url(r'^restore-img/$', views.restore_img),
    url(r'^mypage/$', views.mypage),
    url(r'^mypage-in/$', views.mypage_into_room),
    url(r'^account-inform/$', views.account_inform),
    url(r'^friend-delete/$', views.friend_delete),
    url(r'^myranking/$', views.my_ranking),
    url(r'^delete-user/$',views.delete_user),
    # url(r'^rank-list/$', views.rank_list)
]
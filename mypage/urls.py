from django.urls import path
from .views import *

app_name = 'mypage'

urlpatterns = [
    path('', MyPageView.as_view(), name='mypage-view'),
    path('settings/', NotiSettingView.as_view(), name='notification-settings'), #환경설정 화면 + 알림설정버튼
    path('settings/restrictions/', MyRestrictionListView.as_view(), name='my-restriction-list'),  # 내 제재 이력
    path('settings/feedback/', FeedbackCreateView.as_view(), name='feedback-create'), #피드백 제출
    path('settings/block-user/', MyBlockedUserListView.as_view(), name='my-blocked-list'),
    path('settings/block-user/create/', BlockUserView.as_view(), name='block-user'),
    path('settings/block-user/<int:pk>/', UnblockUserView.as_view(), name='unblock-user'),
]
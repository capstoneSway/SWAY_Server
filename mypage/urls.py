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

    # 관리자용
    path('admin/restrictions/', RestrictionListView.as_view(), name='restriction-list'),  # 전체 제재 목록
    path('admin/restrictions/create/', RestrictionCreateView.as_view(), name='restriction-create'),  # 제재 등록
    path('admin/restrictions/<int:pk>/', RestrictionAdminDetailView.as_view(), name='admin-restriction-detail'),  # 단일 조회/수정/삭제
    path('admin/feedback/', FeedbackListView.as_view(), name='feedback-list'),
    path('admin/feedback/<int:pk>/', FeedbackDetailView.as_view(), name='feedback-detail'),
    path('admin/reports/', ReportListView.as_view(), name='admin-report-list'),
    path('admin/reports/<int:pk>/', ReportDetailView.as_view(), name='admin-report-detail'),
    path('admin/reports/<int:pk>/restrict/', RestrictFromReportView.as_view(), name='restrict-from-report'), #report페이지에서 바로 제재 생성용

]
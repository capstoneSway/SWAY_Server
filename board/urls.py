from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'board'

urlpatterns = [
    path('', BoardList.as_view(), name='board-list'),
    path('create/', BoardCreate.as_view(), name='board-create'),
    path('<int:pk>/', BoardDetail.as_view(),name='board-detail'),
    path('<int:board_id>/block-user/', AddBlockUserView.as_view(),name='block-board-user'),
    path('<int:board_id>/comments/', CommentList.as_view(), name='comment-list-create'),
    path('<int:board_id>/update/', BoardUpdate.as_view(), name='board-update'),
    path('<int:board_id>/comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
    path('<int:board_id>/comments/<int:comment_id>/block-user/', AddBlockCommentUserView.as_view(), name='block-comment-user'),
    path('<int:board_id>/like/', BoardLikeToggleView.as_view()),
    path('<int:board_id>/comments/<int:comment_id>/like/', CommentLikeToggleView.as_view()),
    path('<int:board_id>/scrap/', BoardScrapToggleView.as_view()),
    path('<int:board_id>/report/', BoardReportView.as_view(), name='board-report'),
    path('<int:board_id>/comments/<int:comment_id>/report/', CommentReportView.as_view(), name='comment-report'),
    path('<int:board_id>/noti-toggle/', BoardNotiToggleView.as_view()),
    path('<int:board_id>/comments/<int:comment_id>/noti-toggle/', CommentNotiToggleView.as_view()),

]
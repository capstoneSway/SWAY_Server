from django.urls import path, include
from .views import BoardList, BoardCreate, BoardDetail, CommentDetail, CommentList
from django.conf import settings
from django.conf.urls.static import static

app_name = 'board'

urlpatterns = [
    path('', BoardList.as_view(), name='board-list'),
    path('create/', BoardCreate.as_view(), name='board-create'),
    path('<int:pk>/', BoardDetail.as_view(),name='board-detail'),
    path('<int:board_id>/comments/', CommentList.as_view(), name='comment-list-create'),
    path('<int:board_id>/comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
# 게시글 별 댓글 조회용
    path('<int:board_id>/comments/', CommentList.as_view(), name='board-comments'),


    path('<int:board_id>/comments/<int:pk>/', CommentDetail.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }),name='comment-detail'),
"""
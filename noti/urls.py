from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationAsRead,
    MarkAllNotificationsAsRead,
    UnreadNotificationCountView,
    DeleteNotificationView,
    DeleteAllNotificationsView
)
from .views import PushTestView

app_name = 'noti'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('test-push/', PushTestView.as_view(), name='test-push'),
    path('<int:pk>/read/', MarkNotificationAsRead.as_view(), name='notification-read'),
    path('read-all/', MarkAllNotificationsAsRead.as_view(), name='notification-read-all'),
    path('unread-count/', UnreadNotificationCountView.as_view(), name='notification-unread-count'),
    path('<int:pk>/delete/', DeleteNotificationView.as_view(), name='notification-delete'),
    path('delete-all/', DeleteAllNotificationsView.as_view(), name='notification-delete-all'),
]
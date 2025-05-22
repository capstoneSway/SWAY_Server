from django.urls import path
from .views import MessageListView, chat_room_view

urlpatterns = [
    path('messages/<int:room_id>/', MessageListView.as_view(), name='chat-message-list'),
    path('room/<int:lightning_id>/', chat_room_view, name='chat-room-html'),
]
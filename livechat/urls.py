from django.urls import path
from .views import MessageListView, chat_room_view, ChatImageUploadView, LeaveChatRoomView

urlpatterns = [
    path('messages/<int:room_id>/', MessageListView.as_view(), name='chat-message-list'),
    path('room/<int:lightning_id>/', chat_room_view, name='chat-room-html'),
    path('upload/<int:room_id>/', ChatImageUploadView.as_view(), name='chat-image-upload'),
    path('room/<int:room_id>/leave/', LeaveChatRoomView.as_view(), name='leave_chat_room'),
]
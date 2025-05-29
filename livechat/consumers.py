import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import LiveChatRoom, LiveChatMessage
from lightning.models import Lightning
from django.contrib.auth import get_user_model
from noti.fcm import send_fcm_notification
from accounts.models import User
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user', None)
        if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
            print("⛔ WebSocket connection refused: Unauthenticated user")
            await self.close()
            return

        self.user = user
        print(f"✅ WebSocket connected: {self.user.nickname}")

        self.lightning_id = self.scope['url_route']['kwargs']['lightning_id']
        self.room_group_name = f'chat_{self.lightning_id}'

        # 그룹에 가입
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data): # 메시지 수신
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']

        room = await self.get_chat_room(self.lightning_id)
        await self.create_message(room, sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': {
                    'nickname': sender.nickname,
                    'profile_image': sender.profile_image,
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def get_chat_room(self, lightning_id):
        return LiveChatRoom.objects.get(lightning_id=lightning_id)

    @database_sync_to_async
    def create_message(self, room, sender, message):
        participants = room.participants.exclude(id=sender.id)
        for user in participants:
            if user.fcm_token:
                async_to_sync(send_fcm_notification)(
                    token=user.fcm_token,
                    title="새 채팅 도착",
                    body=f"{sender.nickname or sender.email}님의 메시지: {message}"
                )
        return LiveChatMessage.objects.create(room=room, sender=sender, message=message)
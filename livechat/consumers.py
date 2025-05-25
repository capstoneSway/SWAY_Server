import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import LiveChatRoom, LiveChatMessage
from lightning.models import Lightning
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
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
        # message = data['message']
        message = data.get('message') # 메시지 내용(없으면 None)
        image_url = data.get('image_url') # 이미지 주소(없으면 None)
        sender = self.scope['user']

        room = await self.get_chat_room(self.lightning_id)

        # ✅ DB에 저장: 이미지 또는 메시지가 있을 경우에만 저장
        if message or image_url:
            await self.create_message(room, sender, message, image_url)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'image_url': image_url,
                    'sender': sender.nickname or sender.email
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image_url': event['image_url'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def get_chat_room(self, lightning_id):
        return LiveChatRoom.objects.get(lightning_id=lightning_id)

    @database_sync_to_async
    def create_message(self, room, sender, message=None, image_url=None):
        return LiveChatMessage.objects.create(room=room, sender=sender, message=message or '', picture=image_url)
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
    # WebSocket 연결 요청 처리
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

    # WebSocket 연결 종료 처리
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # # 클라이언트로부터 수신한 WebSocket 메시지를 처리
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        image_url = data.get("image_url", None)
        sender = self.scope['user']

        # ❗️내용이 없으면 저장하지 않음
        if not message and not image_url:
            return

        # 채팅방 정보 가져오기
        room = await self.get_chat_room(self.lightning_id)
        # ✅ 텍스트 메시지일 때만 DB에 저장
        if message:
            chat_message = await self.create_message(room, sender, message)
        # FCM 푸시 전송 (동기 함수이므로 await 사용 금지)
        participants = await self.get_participants(room, sender)
        for user in participants:
            if user.fcm_token:
                send_fcm_notification(
                    token=user.fcm_token,
                    title="새 채팅 도착",
                    body=f"{sender.nickname or sender.email}님의 메시지: {message}"
                )
        # WebSocket 메시지 브로드캐스트만 수행
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                "image_url": image_url,
                'sender': {
                    'nickname': sender.nickname,
                    'profile_image': sender.profile_image,
                    'nationality': sender.nationality,
                    'national_code': sender.national_code,
                }
            }
        )

    # 그룹 메시지를 클라이언트에게 전송하는 핸들러
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image_url': event.get('image_url'),
            'sender': event['sender']
        }))

    # lightning_id를 기반으로 채팅방 객체를 가져오는 함수
    # WebSocket 연결 시 채팅방 정보를 조회할 때 사용
    @database_sync_to_async
    def get_chat_room(self, lightning_id):
        return LiveChatRoom.objects.get(lightning_id=lightning_id)

    # 채팅 메시지를 DB에 저장하는 함수
    # sender가 보낸 텍스트 메시지를 LiveChatMessage 모델에 저장
    @database_sync_to_async
    def create_message(self, room, sender, message):
        return LiveChatMessage.objects.create(room=room, sender=sender, message=message)

    # 현재 메시지를 보낸 사용자를 제외한 채팅방 참가자 목록을 가져오는 함수
    # FCM 푸시 알림 등을 보낼 대상 필터링용
    @database_sync_to_async
    def get_participants(self, room, sender):
        return list(room.participants.exclude(id=sender.id))

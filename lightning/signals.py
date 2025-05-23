from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Lightning
from livechat.models import LiveChatRoom

# 1) 번개모임 생성 시 → 채팅방 생성 + host를 채팅방 참가자로 등록
@receiver(post_save, sender=Lightning)
def create_chat_room(sender, instance, created, **kwargs):
    if created:
        chat_room = LiveChatRoom.objects.create(lightning=instance, host=instance.host)
        chat_room.participants.add(instance.host)

# 2) 번개모임 참가자 변경 시 → 채팅방 참가자와 동기화
@receiver(m2m_changed, sender=Lightning.participants.through)
def sync_chat_participants(sender, instance, action, pk_set, **kwargs):
    try:
        chat_room = instance.chat_room
    except LiveChatRoom.DoesNotExist:
        return

    if action == "post_add":
        # 참가자가 모임에 추가될 때 → 채팅방에도 추가
        for user_id in pk_set:
            chat_room.participants.add(user_id)

    elif action == "post_remove":
        # 참가자가 모임에서 제거될 때 → 채팅방에서도 제거
        for user_id in pk_set:
            chat_room.participants.remove(user_id)
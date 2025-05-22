from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lightning
from livechat.models import LiveChatRoom

@receiver(post_save, sender=Lightning)
def create_chat_room(sender, instance, created, **kwargs):
    if created:
        LiveChatRoom.objects.create(lightning=instance, host=instance.host)
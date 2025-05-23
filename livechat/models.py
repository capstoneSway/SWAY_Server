from django.db import models
from django.conf import settings
from lightning.models import Lightning

# Create your models here.
class LiveChatRoom(models.Model):
    lightning = models.OneToOneField(Lightning, on_delete=models.CASCADE, related_name='chat_room')
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_chat_rooms')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_chat_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lightning.title} ChatRoom"

class LiveChatMessage(models.Model):
    room = models.ForeignKey(LiveChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    picture = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.message}"
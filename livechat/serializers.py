from rest_framework import serializers
from .models import LiveChatMessage

class LiveChatMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)

    class Meta:
        model = LiveChatMessage
        fields = ['id', 'room', 'sender_email', 'message', 'picture', 'created_at']
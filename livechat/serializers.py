from rest_framework import serializers
from .models import LiveChatMessage
from django.conf import settings

class LiveChatMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    picture_url = serializers.SerializerMethodField()

    def get_picture_url(self, obj):
        if obj.picture:
            return f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{obj.picture.name}"
        return None

    class Meta:
        model = LiveChatMessage
        fields = ['id', 'room', 'sender_email', 'message', 'picture', 'picture_url', 'created_at']
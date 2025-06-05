from rest_framework import serializers
from .models import LiveChatMessage
from accounts.utils import get_profile_image_url
from django.conf import settings
from accounts.models import User

class SenderInfoSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        return get_profile_image_url(obj)

    class Meta:
        model = User
        fields = ['nickname', 'profile_image', 'nationality', 'national_code']

class LiveChatMessageSerializer(serializers.ModelSerializer):
    sender_info = SenderInfoSerializer(source='sender', read_only=True)
    # sender_email = serializers.EmailField(source='sender.email', read_only=True) #아래 field에도 sender_email 추가
    picture_url = serializers.SerializerMethodField()

    def get_picture_url(self, obj):
        if obj.picture:
            return f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{obj.picture.name}"
        return None

    class Meta:
        model = LiveChatMessage
        fields = ['id', 'room', 'sender_info', 'message', 'picture', 'picture_url', 'created_at']
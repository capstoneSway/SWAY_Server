from rest_framework import serializers
from .models import Lightning
from accounts.utils import get_profile_image_url
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()


class ParticipantSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        return get_profile_image_url(obj)

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'email', 'profile_image', 'nationality', 'national_code']


class LightningSerializer(serializers.ModelSerializer):
    host = ParticipantSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lightning
        fields = '__all__'
        read_only_fields = ['id', 'host', 'created_at']


class LightningDetailSerializer(serializers.ModelSerializer):
    host = ParticipantSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lightning
        fields = '__all__'
        read_only_fields = ['id', 'host', 'created_at', 'like', 'current_participant']
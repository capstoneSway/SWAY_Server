from rest_framework import serializers
from .models import Lightning, LightningParticipation
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image']


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

class LightningParticipationSerializer(serializers.ModelSerializer):
    lightning = LightningSerializer(read_only=True)  # 또는 LightningDetailSerializer도 가능
    relation_tag = serializers.CharField(source='get_relation_tag_display')  # 보기 좋게 한국어로 반환

    class Meta:
        model = LightningParticipation
        fields = ['lightning', 'relation_tag']
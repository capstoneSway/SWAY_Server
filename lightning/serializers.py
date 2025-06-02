from rest_framework import serializers
from .models import Lightning, LightningParticipation
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

class LightningParticipationSerializer(serializers.ModelSerializer):
    relation_tag = serializers.CharField(source='get_relation_tag_display') 

    class Meta:
        model = LightningParticipation
        fields = ['relation_tag']

class ParticipantSerializer(serializers.ModelSerializer):
    relation_tag = LightningParticipationSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'nationality', 'national_code', 'relation_tag']



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



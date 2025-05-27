from rest_framework import serializers
from .models import Lightning

class LightningSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField(read_only=True)
    participants = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Lightning
        fields = ['id', 'host', 'title', 'created_at', 'end_time', 'participants', 'current_participant']
        read_only_fields = ['id', 'host', 'created_at', 'current_participant']

class LightningDetailSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField(read_only=True)
    participants = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Lightning
        fields = '__all__'
        read_only_fields = ['id', 'host', 'created_at', 'like', 'current_participant']


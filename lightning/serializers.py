from rest_framework import serializers
from .models import Lightning

class LightningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lightning
        fields = '__all__'
        read_only_fields = ['id', 'host', 'created_at', 'like', 'current_participant']
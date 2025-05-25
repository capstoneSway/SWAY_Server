from rest_framework import serializers
from .models import ExchangeRate, ExchangeMemo

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = '__all__'

class ExchangeMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeMemo
        fields = '__all__'
        read_only_fields = ['user', 'date']
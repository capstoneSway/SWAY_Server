from rest_framework import serializers
from .models import ExchangeRate, ExchangeMemo

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = '__all__'
        # fields = ['cur_unit', 'cur_nm', 'ttb', 'tts', 'deal_bas_r', 'bkpr', 'y_efee_r', 'ten_d_efee_r', 'kftc_deal_bas_r', 'kftc_bkpr', 'date']

class ExchangeMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeMemo
        fields = '__all__'
        read_only_fields = ['user', 'date']
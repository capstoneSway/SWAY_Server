from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': "Token is expired or invalid"
    }

    # def validate(self, attrs):
    #     self.token = attrs['refresh']
    #     return attrs

    # def save(self, **kwargs):
    #     try:
    #         RefreshToken(self.token).blacklist()
    #     except TokenError:
    #         self.fail('bad_token')
    
    def validate_refresh(self, value):
        try:
            RefreshToken(value)  # 유효성 검사
        except TokenError:
            self.fail('bad_token')
        return value

    def save(self, **kwargs):
        refresh_token = self.validated_data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')

class NicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']

class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nationality', 'national_code']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']
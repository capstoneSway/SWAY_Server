from rest_framework import serializers
from .models import User
from django.conf import settings
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

# ✅ 사용자 정보 조회 시: 통합된 profile_image_url 필드 반환
class UserSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    def get_profile_image_url(self, obj):
            if obj.profile_image_changed:
                return f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{obj.profile_image_changed.name}"
            elif obj.profile_image:
                return obj.profile_image
            return None
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'nickname',
            'gender',
            'nationality',
            'profile_image_url',
        ]

# ✅ SWAY 앱에서 사용자가 직접 업로드한 프로필 이미지 수정용
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'profile_image_changed']
# mypage/serializers.py
from rest_framework import serializers
from .models import *
from accounts.utils import get_profile_image_url
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
'''
class MyPageSerializer(serializers.Serializer):
    #다른 시리얼라이저에서 가져와도 충분해서 미사용예정
    my_posts = BoardSerializer(many=True, read_only=True)
    scrapped_posts = BoardSerializer(many=True, read_only=True)
    lightning_meetings = LightningSerializer(many=True)
'''

class NotiSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotiSetting
        fields = ['comment_noti', 'reply_noti', 'meetup_noti', 'chat_noti']

class RestrictionSerializer(serializers.ModelSerializer):
    restriction_type_display = serializers.CharField(source='get_restriction_type_display', read_only=True)
    is_active = serializers.SerializerMethodField()
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    release_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Restriction
        fields = ['id', 'user', 'nickname', 'reason', 'restriction_type', 'restriction_type_display', 'created_at', 'duration_days', 'release_at', 'is_active']
        read_only_fields = ['id', 'nickname', 'restriction_type_display', 'created_at', 'release_at', 'is_active']

    def get_is_active(self, obj):
        return obj.is_active()

class FeedbackSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'nickname' ,'feedback_type', 'title', 'content', 'submitted_at']
        read_only_fields = ['id', 'user', 'nickname', 'submitted_at']


class BlockUserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(write_only=True)

    class Meta:
        model = BlockUser
        fields = ['id', 'nickname', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_nickname(self, value):
        try:
            blocked_user = get_user_model().objects.get(nickname=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("A user with this nickname does not exist.")

        if blocked_user == self.context['request'].user:
            raise serializers.ValidationError("You cannot block yourself.")

        if BlockUser.objects.filter(user=self.context['request'].user, blocked_user=blocked_user).exists():
            raise serializers.ValidationError("This user is already blocked.")

        return value

    def create(self, validated_data):
        nickname = validated_data.pop('nickname')
        blocked_user = get_user_model().objects.get(nickname=nickname)
        return BlockUser.objects.create(
            user=self.context['request'].user,
            blocked_user=blocked_user
        )
    
class BlockUserListSerializer(serializers.ModelSerializer):
    blocked_user_id = serializers.IntegerField(source='blocked_user.id', read_only=True)
    nickname = serializers.CharField(source='blocked_user.nickname', read_only=True)
    nationality = serializers.CharField(source='blocked_user.nationality', read_only=True)
    profile_image = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        return get_profile_image_url(obj.blocked_user)
    
    class Meta:
        model = BlockUser
        fields = ['id', 'blocked_user_id', 'nickname', 'profile_image', 'nationality', 'created_at']


from rest_framework import serializers
from .models import *
from accounts.utils import get_profile_image_url
from mypage.models import BlockUser
from django.conf import settings

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    board_id = serializers.IntegerField(source='board.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.SerializerMethodField()
    nationality = serializers.CharField(source='user.nationality', read_only=True)
    parent_username = serializers.SerializerMethodField()
    parent_nickname = serializers.SerializerMethodField()
    comment_is_liked = serializers.SerializerMethodField() #commentlikes
    like_count = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        return get_profile_image_url(obj.user)
    
    def get_parent_id(self, obj):
        return obj.parent.id if obj.parent else None
    
    def get_parent_username(self, obj):
        return obj.parent.user.username if obj.parent else None

    def get_parent_nickname(self, obj):
        return obj.parent.user.nickname if obj.parent else None

    class Meta:
        model = Comment
        fields = ('id', 'username', 'nickname', 'profile_image', 'nationality', 
            'board_id', 'date', 'parent_id',
            'parent_username', 'parent_nickname', 'is_blocked', 'is_deleted', 'content', 'comment_is_liked','like_count', 'reply')
        read_only_fields = [
            'id', 'user', 'username', 'nickname', 'profile_image', 'nationality', 'board_id',
            'date', 'parent_username', 'parent_nickname', 'is_blocked',
            'like_count', 'reply'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH'] and 'parent' in self.fields:
            # 수정 요청일 경우 parent 필드를 읽기 전용으로
            self.fields['parent'].read_only = True
            
    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return BlockUser.objects.filter(user=request.user, blocked_user=obj.user).exists()
        return False
    
    def get_comment_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.commentlikes.filter(user=request.user).exists()
        return False

    def get_like_count(self, obj):
        return obj.commentlikes.count()
    
    def get_reply(self, instance):
        replies = instance.reply.all()

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            blocked_ids = BlockUser.objects.filter(user=request.user).values_list('blocked_user', flat=True)
            replies = replies.exclude(user__in=blocked_ids)

        serializer = self.__class__(replies, many=True, context=self.context)
        serializer.bind('', self)
        return serializer.data
    
    def create(self, validated_data):
        parent_id = self.initial_data.get('parent_id')
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id)
                validated_data['parent'] = parent
                validated_data['parent_user'] = parent.user  # parent_user도 자동 설정
            except Comment.DoesNotExist:
                raise serializers.ValidationError({'parent_id': 'Invalid parent comment ID.'})
        return super().create(validated_data)

    '''
        def get_reply(self, instance):
    	# recursive
        serializer = self.__class__(instance.reply, many=True)
        serializer.bind('', self)
        return serializer.data
    '''

# 디테일 페이지에서 재귀문 제거를 위해 따로 작성 / 읽기전용
class CommentDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.SerializerMethodField()
    nationality = serializers.CharField(source='user.nationality', read_only=True)
    board_id = serializers.IntegerField(source='board.id', read_only=True)
    parent = serializers.SerializerMethodField()
    parent_nickname = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        return get_profile_image_url(obj.user)
    
    def get_parent(self, obj):
        return obj.parent.id if obj.parent else None
    
    def get_parent_nickname(self, obj):
        return obj.parent.user.nickname if obj.parent else None
    
    class Meta:
        model = Comment
        fields = ('id', 'username','nickname', 'profile_image', 'nationality', 'board_id' ,'date', 'is_deleted', 'parent', 'parent_nickname', 'content')
        read_only_fields = [
            'id', 'user', 'username', 'nickname', 'profile_image', 'nationality', 'board_id',
            'date', 'parent_nickname']

class BoardImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            return f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{obj.image.name}"
        return None

    class Meta:
        model = BoardImage
        fields = ['id', 'image', 'image_url']

class BoardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    scrap_count = serializers.SerializerMethodField()
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.SerializerMethodField()
    nationality = serializers.CharField(source='user.nationality', read_only=True)
    images = BoardImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_scraped = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        return get_profile_image_url(obj.user)

    class Meta:
        model = Board
        fields = ['id', 'username', 'nickname', 'profile_image', 'nationality', 'title', 'content', 'images', 'date', 'comment_count', 'like_count', 'scrap_count', 'is_liked', 'is_scraped']
        read_only_fields = ['id', 'user', 'username', 'nickname', 'profile_image', 'nationality', 'date', 'comment_count', 'like_count', 'scrap_count', 'is_liked', 'is_scraped']

    def get_comment_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_scrap_count(self, obj):
        return obj.scraps.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_scraped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.scraps.filter(user=request.user).exists()
        return False

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
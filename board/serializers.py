from rest_framework import serializers
from .models import Board, Comment, Report
from mypage.models import BlockUser

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(write_only=True, required=False)  # 그냥 숫자 받기
    reply = serializers.SerializerMethodField()
    board_id = serializers.IntegerField(source='board.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.URLField(source='user.profile_image', read_only=True)
    parent_username = serializers.CharField(source='parent_user.username', read_only=True)
    parent_nickname = serializers.CharField(source='parent_user.nickname', read_only=True)
    like_count = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ('id', 'username', 'nickname', 'profile_image', 
            'board_id', 'date', 'parent_id',
            'parent_username', 'parent_nickname', 'content', 'like_count', 'reply')
        read_only_fields = [
            'id', 'user', 'username', 'nickname', 'profile_image', 'board_id',
            'date', 'parent_username', 'parent_nickname',
            'like_count', 'reply'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']:
            # 수정 요청일 경우 parent 필드를 읽기 전용으로
            self.fields['parent'].read_only = True

    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_reply(self, instance):
        replies = instance.reply.all()

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            blocked_ids = BlockUser.objects.filter(user=request.user).values_list('blocked_user', flat=True)
            replies = replies.exclude(user__in=blocked_ids)

        serializer = self.__class__(replies, many=True, context=self.context)
        serializer.bind('', self)
        return serializer.data

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
    profile_image = serializers.URLField(source='user.profile_image', read_only=True)
    board_id = serializers.IntegerField(source='board.id', read_only=True)
    parent = serializers.IntegerField(source='parent.id', read_only=True)
    parent_nickname = serializers.CharField(source='parent_user.nickname', read_only=True)
    class Meta:
        model = Comment
        fields = ('id', 'username','nickname', 'profile_image', 'board_id' ,'date', 'parent', 'parent_nickname', 'content')
        read_only_fields = [
            'id', 'user', 'username', 'nickname', 'profile_image', 'board_id',
            'date', 'parent_nickname']

class BoardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.SerializerMethodField()
    scrap_count = serializers.SerializerMethodField()
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.URLField(source='user.profile_image', read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'username', 'nickname', 'profile_image', 'title', 'content', 'image', 'date', 'like_count', 'scrap_count']
        read_only_fields = ['id', 'user', 'username', 'nickname', 'profile_image', 'date', 'like_count', 'scrap_count']
    
    def get_like_count(self, obj):
        return obj.likes.count()

    def get_scrap_count(self, obj):
        return obj.scraps.count()
    

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'board', 'comment', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


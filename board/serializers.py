from rest_framework import serializers
from .models import Board, Comment

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    reply = serializers.SerializerMethodField()
    board = serializers.SlugRelatedField(read_only=True, slug_field='title')
    user = serializers.StringRelatedField(read_only=True)
    parent_user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ('id', 'user', 'board', 'created_at', 'parent', 'parent_user', 'comment', 'reply')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']:
            # 수정 요청일 경우 parent 필드를 읽기 전용으로
            self.fields['parent'].read_only = True
    
    def get_reply(self, instance):
    	# recursive
        serializer = self.__class__(instance.reply, many=True)
        serializer.bind('', self)
        return serializer.data

# 디테일 페이지에서 재귀문 제거를 위해 따로 작성 / 읽기전용
class CommentDetailSerializer(serializers.ModelSerializer):
    board = serializers.SlugRelatedField(read_only=True, slug_field='title')
    parent_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'board' ,'created_at', 'parent', 'parent_user', 'comment')


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'user', 'title', 'body', 'image', 'date']
        read_only_fields = ['user']

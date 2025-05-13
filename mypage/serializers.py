# mypage/serializers.py
from rest_framework import serializers
#from board.models import Board
from board.serializers import BoardSerializer  # 게시판 글 요약용 시리얼라이저 사용

class MyPageSerializer(serializers.Serializer):
    my_posts = BoardSerializer(many=True, read_only=True)
    scrapped_posts = BoardSerializer(many=True, read_only=True)
    # 추후 lightning_meetings = LightningMeetingSerializer(many=True) 등 추가 가능

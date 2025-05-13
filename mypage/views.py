from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from board.models import Board
from board.serializers import BoardSerializer
from rest_framework.response import Response

# Create your views here.
class MyPageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        my_posts = Board.objects.filter(user=user)
        scrapped_posts = Board.objects.filter(scraps__user=user)

        return Response({
            "my_posts": BoardSerializer(my_posts, many=True).data,
            "scrapped_posts": BoardSerializer(scrapped_posts, many=True).data,
        }) #추후 번개모임 추가 필요 / 앱 분할
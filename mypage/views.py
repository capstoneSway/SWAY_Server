from .models import *
from .serializers import *
from board.models import Board, Report
from board.serializers import BoardSerializer, ReportSerializer
from lightning.models import Lightning
from lightning.serializers import LightningSerializer
from rest_framework import filters
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

# Create your views here.
class MyPageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        participanted_lightening = Lightning.objects.filter(participants=user)
        my_posts = Board.objects.filter(user=user)
        scrapped_posts = Board.objects.filter(scraps__user=user)

        return Response({
            "participanted_lightening": LightningSerializer(participanted_lightening, many=True).data,
            "my_posts": BoardSerializer(my_posts, many=True).data,
            "scrapped_posts": BoardSerializer(scrapped_posts, many=True, context={'request': request}),
        })
    
class NotiSettingView(RetrieveUpdateAPIView):
    serializer_class = NotiSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 로그인한 유저의 NotificationSetting 가져오기 (없으면 자동 생성)
        obj, created = NotiSetting.objects.get_or_create(
            user=self.request.user,
            defaults={
                'post_noti': True,
                'comment_noti': True,
                'meetup_noti': True,
                'chat_noti': True,
            })
        return obj
    

class MyRestrictionListView(ListAPIView):
    serializer_class = RestrictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Restriction.objects.filter(user=self.request.user).order_by('-created_at')




class FeedbackCreateView(CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyBlockedUserListView(ListAPIView):
    serializer_class = BlockUserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockUser.objects.filter(user=self.request.user).select_related('blocked_user')

class BlockUserView(CreateAPIView):
    queryset = BlockUser.objects.all()
    serializer_class = BlockUserSerializer
    permission_classes = [IsAuthenticated]

class UnblockUserView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockUser.objects.filter(user=self.request.user)



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
            "scrapped_posts": BoardSerializer(scrapped_posts, many=True).data,
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
    

class RestrictionListView(ListAPIView): #관리자전용
    queryset = Restriction.objects.all().order_by('-created_at')
    serializer_class = RestrictionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__nickname']

class MyRestrictionListView(ListAPIView):
    serializer_class = RestrictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Restriction.objects.filter(user=self.request.user).order_by('-created_at')

class RestrictionCreateView(CreateAPIView): #관리자전용
    queryset = Restriction.objects.all()
    serializer_class = RestrictionSerializer
    permission_classes = [IsAdminUser]

class RestrictionAdminDetailView(RetrieveUpdateDestroyAPIView): #관리자전용
    queryset = Restriction.objects.all()
    serializer_class = RestrictionSerializer
    permission_classes = [IsAdminUser]



class FeedbackCreateView(CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FeedbackListView(ListAPIView):  # 관리자 전용
    queryset = Feedback.objects.all().order_by('-submitted_at')
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'user__username']


class FeedbackDetailView(RetrieveAPIView):  # 관리자 전용
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUser]

class ReportListView(ListAPIView):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]

class ReportDetailView(RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]

class RestrictFromReportView(CreateAPIView):
    serializer_class = RestrictionSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        report_id = self.kwargs['pk']
        report = get_object_or_404(Report, pk=report_id)

        if report.board:
            target_user = report.board.user
        elif report.comment:
            target_user = report.comment.user
        else:
            raise ValidationError("Report has no valid target.")

        serializer.save(user=target_user)


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



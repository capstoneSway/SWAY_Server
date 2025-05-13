from rest_framework import generics, permissions
from .models import Lightning
from .serializers import LightningSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from noti.models import Notification, NotificationType

# 전체 목록 조회 (모든 사용자 가능)
class LightningList(generics.ListAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.AllowAny]

# 생성 (로그인된 사용자만 가능)
class LightningCreate(generics.CreateAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        lightning = serializer.save(host=self.request.user)
        lightning.participants.add(self.request.user)
        lightning.current_participatn = lightning.participants.count()
        lightning.save() # 주최자는 현재 로그인한 유저

# 상세 조회 (모든 사용자 가능)
class LightningDetail(generics.RetrieveAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.AllowAny]

# 수정 (로그인 + 작성자 본인만 가능)
class LightningUpdate(generics.UpdateAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user != self.get_object().host:
            raise PermissionDenied("수정 권한이 없습니다.")
        serializer.save()

# 삭제 (로그인 + 작성자 본인만 가능)
class LightningDelete(generics.DestroyAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user != instance.host:
            raise PermissionDenied("삭제 권한이 없습니다.")
        
         # 알림 전송: 참가자들에게 번개 취소 알림
        for participant in instance.participants.all():
            Notification.objects.create(
                user=participant,
                type='번개모임',
                event=instance,
                message=f"[{instance.title}] 번개가 취소되었어요.",
            )
            
        instance.delete()

# 참가자의 번개 신청
class JoinLightning(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        lightning = get_object_or_404(Lightning, pk=pk)
        user = request.user

        if lightning.participants.filter(id=user.id).exists():
            raise ValidationError("이미 참가한 번개입니다.")
        if lightning.participants.count() >= lightning.max_participant:
            raise ValidationError("참가 인원이 초과되었습니다.")
        
        lightning.participants.add(user)
        lightning.current_participant += 1
        lightning.save()

        Notification.objects.create(
            user = lightning.host,
            type = "번개모임",
            event = f"{user.username}님이 [{lightning.title}] 번개에 참가했어요."
        )

        return Response({"message": "참가 신청이 완료되었습니다."})
    

# 참가자의 번개 취소
class LeaveLightning(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        lightning = get_object_or_404(Lightning, pk=pk)
        user = request.user

        if not lightning.participants.filter(id=user.id).exists():
            raise ValidationError("참가하지 않은 번개입니다.")

        lightning.participants.remove(user)
        lightning.current_participant -= 1
        lightning.save()

        # 알림 생성: 참가자가 취소했음을 호스트에게
        Notification.objects.create(
            user=lightning.host,
            type='번개모임',
            event=lightning,
            message=f"{user.username}님이 [{lightning.title}] 번개 참가를 취소했어요.",
        )

        return Response({"message": "참가가 취소되었습니다."})
from rest_framework import generics, permissions
from .models import Lightning, LightningParticipation, Tag
from .serializers import LightningSerializer, LightningDetailSerializer, ParticipantSerializer, LightningParticipationSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from noti.models import Notification
from noti.fcm import send_fcm_notification
from django.db.models import Q

# 전체 목록 조회 (모든 사용자 가능)
class LightningList(generics.ListAPIView):
    queryset = Lightning.objects.filter(is_active=True)
    serializer_class = LightningSerializer
    permission_classes = [permissions.AllowAny]

# 상세 조회 (모든 사용자 가능)
class LightningDetail(generics.RetrieveAPIView):
    queryset = Lightning.objects.filter(is_active=True)
    serializer_class = LightningDetailSerializer
    permission_classes = [permissions.AllowAny]

# 카테고리별 조회 (모든 사용자 가능)
class LightningCategoryFilterView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        queryset = Lightning.objects.filter(category=category, is_active=True)
        serializer = LightningSerializer(queryset, many=True)
        return Response(serializer.data)

# 상태별 조회 (모든 사용자 가능)
class LightningStatusFilterView(APIView):
    def get(self, request):
        status = request.query_params.get('status')
        queryset = Lightning.objects.filter(status=status, is_active=True)
        serializer = LightningSerializer(queryset, many=True)
        return Response(serializer.data)

# 생성 (로그인된 사용자만 가능)
class LightningCreate(generics.CreateAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        lightning = serializer.save(host=self.request.user)

        LightningParticipation.objects.create(
            user=self.request.user,
            lightning=lightning,
            relation_tag=Tag.HOSTED
        )

        lightning.current_participant = lightning.participants.count()
        lightning.update_status()

    

# 수정 (로그인 + 작성자 본인만 가능)
class LightningUpdate(generics.UpdateAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        lightning = self.get_object()

        if self.request.user != lightning.host:
            raise PermissionDenied("수정 권한이 없습니다.")

        new_max = serializer.validated_data.get('max_participant', lightning.max_participant)

        if new_max < lightning.current_participant:
            raise ValidationError(
                f"현재 참여 중인 인원({lightning.current_participant})보다 적게 설정할 수 없습니다."
            )

        serializer.save()
        lightning.refresh_from_db()
        lightning.update_status()

# 삭제 (로그인 + 작성자 본인만 가능)
class LightningDelete(generics.DestroyAPIView):
    queryset = Lightning.objects.filter(is_active=True)
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user != instance.host:
            raise PermissionDenied("삭제 권한이 없습니다.")
        
        # 호스트에게 알림
        Notification.objects.create(
            user=instance.host,
            type='번개모임',
            event=instance,
            message=f"[{instance.title}] 번개가 삭제되었어요.",
        )
        
        # 참가자(호스트 제외)들에게 알림
        participants = instance.participants.exclude(id=instance.host.id)
        for participant in participants:
            Notification.objects.create(
                user=participant,
                type='번개모임',
                event=instance,
                message=f"[{instance.title}] 번개가 취소되었어요.",
            )

        # 상태 비활성화 처리
        instance.is_active = False
        instance.status = instance.Status.CANCELED
        instance.save()

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
        lightning.update_status()

        participation, created = LightningParticipation.objects.get_or_create(
            user=user,
            lightning=lightning,
            defaults={'relation_tag': Tag.PARTICIPATED}
        )
        if not created:
            participation.relation_tag = Tag.PARTICIPATED
            participation.save()

        # 알림 생성: 참가자가 번개 모임에 참가했음을 호스트에게 알림
        Notification.objects.create(
            user = lightning.host,
            type = "번개모임",
            event = f"{user.username}님이 [{lightning.title}] 번개에 참가했어요."
        )

        # 푸시 알림 전송: 호스트에게
        if lightning.host.fcm_token:
            send_fcm_notification(
                token=lightning.host.fcm_token,
                title="번개 참가 알림",
                body=f"{user.username}님이 [{lightning.title}] 번개에 참가했어요."
            )

        participants = lightning.participants.all()
        serialized_participants = ParticipantSerializer(participants, many=True).data

        return Response({
            "message": "참가 신청이 완료되었습니다.", 
            "participants": serialized_participants
            }, status=200)
    

# 참가자의 번개 취소
class LeaveLightning(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        lightning = get_object_or_404(Lightning, pk=pk)
        user = request.user

        # 호스트는 참가 취소 불가 (삭제만 가능)
        if lightning.host == user:
            raise ValidationError("호스트는 참가 취소할 수 없습니다. 번개를 삭제해주세요.")

        # 참가 여부 확인
        if not lightning.participants.filter(id=user.id).exists():
            raise ValidationError("참가하지 않은 번개입니다.")

        # 참가 취소 로직
        lightning.participants.remove(user)
        lightning.current_participant -= 1
        lightning.update_status()

        participation = LightningParticipation.objects.filter(user=user, lightning=lightning).first()
        if participation:
            participation.relation_tag = Tag.IRRELEVANT
            participation.save()

        # 알림 : 호스트에게 참가 취소 알림
        Notification.objects.create(
            user=lightning.host,
            type='번개모임',
            event=lightning,
            message=f"{user.username}님이 [{lightning.title}] 번개 참가를 취소했어요.",
        )

        # 푸시 알림 전송: 호스트에게
        if lightning.host.fcm_token:
            send_fcm_notification(
                token=lightning.host.fcm_token,
                title="번개 참가 취소 알림",
                body=f"{user.username}님이 [{lightning.title}] 번개 참가를 취소했어요."
            )

        participants = lightning.participants.all()
        serialized_participants = ParticipantSerializer(participants, many=True).data

        return Response({
            "message": "참가가 취소되었습니다.",
            "participants": serialized_participants
            }, status=200)

# 로그인한 사용자의 Current View
class CurrentLightningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lightnings = Lightning.objects.filter(
            is_active=True
        ).filter(
            Q(host=user) | Q(participants=user)
        ).distinct()
        serializer = LightningSerializer(lightnings, many=True)
        return Response(serializer.data)


class HostedLightningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lightnings = Lightning.objects.filter(host=user, is_active=True)
        serializer = LightningSerializer(lightnings, many=True)
        return Response(serializer.data)


class ParticipatedLightningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lightnings = Lightning.objects.filter(
            participants=user,  # ManyToManyField 연결 필드
            is_active=True
        ).exclude(host=user)  # host는 제외
        serializer = LightningSerializer(lightnings, many=True)
        return Response(serializer.data)
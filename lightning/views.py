from rest_framework import generics, permissions
from .models import Lightning
from .serializers import LightningSerializer, LightningDetailSerializer, ParticipantSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from noti.models import Notification
from noti.fcm import send_fcm_notification
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Lightning
from mypage.models import NotiSetting

# 전체 목록 조회 (모든 사용자 가능)
class LightningList(generics.ListAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.AllowAny]

# 상세 조회 (모든 사용자 가능)
class LightningDetail(generics.RetrieveAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningDetailSerializer
    permission_classes = [permissions.AllowAny]

# 카테고리별 조회 (모든 사용자 가능)
class LightningCategoryFilterView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        queryset = Lightning.objects.filter(category=category)
        serializer = LightningSerializer(queryset, many=True)
        return Response(serializer.data)

# 상태별 조회 (모든 사용자 가능)
class LightningStatusFilterView(APIView):
    def get(self, request):
        status = request.query_params.get('status')
        queryset = Lightning.objects.filter(status=status)
        serializer = LightningSerializer(queryset, many=True)
        return Response(serializer.data)

# 생성 (로그인된 사용자만 가능)
class LightningCreate(generics.CreateAPIView):
    queryset = Lightning.objects.all()
    serializer_class = LightningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        lightning = serializer.save(host=self.request.user)
        
        lightning.participants.add(self.request.user)

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
            raise PermissionDenied("You do not have permission to edit.")

        new_max = serializer.validated_data.get('max_participant', lightning.max_participant)

        if new_max < lightning.current_participant:
            raise ValidationError(
                f"You cannot set a value lower than the current number of participants ({lightning.current_participant})."
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
            raise PermissionDenied("You do not have permission to delete.")
        
        # 호스트의 NotiSetting 가져오기
        try:
            host_noti_setting = NotiSetting.objects.get(user=instance.host)
        except NotiSetting.DoesNotExist:
            return Response({"error": "Host's notification settings are not available."}, status=404)

        if host_noti_setting and host_noti_setting.meetup_noti:
            # 호스트에게 알림
            host_message = f"The meetup [{instance.title}] has been deleted."
            Notification.objects.create(
                user=instance.host,
                type='번개모임',
                event=instance,
                message=host_message,
            )
        
        # 참가자(호스트 제외)들에게 알림
        participants = instance.participants.exclude(id=instance.host.id)
        for participant in participants:
            # 참가자의 NotiSetting 가져오기
            try:
                participant_noti_setting = NotiSetting.objects.get(user=participant)
            except NotiSetting.DoesNotExist:
                continue

            if participant_noti_setting and participant_noti_setting.meetup_noti:
                participant_message =  f"The meetup [{instance.title}] has been canceled."
                Notification.objects.create(
                    user=participant,
                    type='번개모임',
                    event=instance,
                    message=participant_message,
                )
                
                if participant.fcm_token:
                    send_fcm_notification(
                        user=participant,
                        token=participant.fcm_token,
                        title="Meetup Deletion",
                        body=participant_message
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

        # 성별 조건 확인
        user_gender = user.gender  # 사용자의 성별
        event_gender = lightning.gender  # 번개 모임의 성별 조건

        # 번개 모임의 성별 조건이 "남자만"이고 사용자가 여성인 경우 참가 불가
        if event_gender == Lightning.Gender.MALE and user_gender != Lightning.Gender.MALE:
            raise ValidationError("You cannot join this lightning event because it's for males only.")
        
        # 번개 모임의 성별 조건이 "여자만"이고 사용자가 남성인 경우 참가 불가
        if event_gender == Lightning.Gender.FEMALE and user_gender != Lightning.Gender.FEMALE:
            raise ValidationError("You cannot join this lightning event because it's for females only.")
        
        # 번개 모임의 성별 조건이 "모두"인 경우 성별에 관계없이 참가 가능
        if event_gender == Lightning.Gender.ALL:
            pass  # 성별에 관계없이 참가 가능

        if lightning.participants.filter(id=user.id).exists():
            raise ValidationError("You have already joined this lightning event.")
        if lightning.participants.count() >= lightning.max_participant:
            raise ValidationError("The number of participants has exceeded the limit.")
        
        lightning.participants.add(user)
        lightning.current_participant += 1
        lightning.save()
        lightning.update_status()

        # 호스트의 NotiSetting 가져오기
        try:
            host_noti_setting = NotiSetting.objects.get(user=lightning.host)
        except NotiSetting.DoesNotExist:
            return Response({"error": "Host's notification settings are not available."}, status=404)

        if host_noti_setting and host_noti_setting.meetup_noti:
        # 알림 생성: 참가자가 번개 모임에 참가했음을 호스트에게 알림
            Notification.objects.create(
                user = lightning.host,
                type = "번개모임",
                event = lightning,
                message = f"{user.nickname} has joined the lightning event [{lightning.title}]."
            )

            # 푸시 알림 전송: 호스트에게
            if lightning.host.fcm_token:
                send_fcm_notification(
                    user=lightning.host,
                    token=lightning.host.fcm_token,
                    title="Meetup Join",
                    body=f"{user.nickname} has joined the lightning event [{lightning.title}]."
                )

        participants = lightning.participants.all()
        serialized_participants = ParticipantSerializer(participants, many=True).data

        return Response({
            "message": "Your application has been completed.", 
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
            raise ValidationError("The host cannot cancel their participation. Please delete the lightning event.")

        # 참가 여부 확인
        if not lightning.participants.filter(id=user.id).exists():
            raise ValidationError("You have not joined this lightning event.")

        # 참가 취소 로직
        lightning.participants.remove(user)
        lightning.current_participant = lightning.current_participant - 1
        lightning.save()
        lightning.update_status()

        # 호스트의 NotiSetting 가져오기
        try:
            host_noti_setting = NotiSetting.objects.get(user=lightning.host)
        except NotiSetting.DoesNotExist:
            return Response({"error": "Host's notification settings are not available."}, status=404)

        if host_noti_setting and host_noti_setting.meetup_noti:
            # 알림 : 호스트에게 참가 취소 알림
            Notification.objects.create(
                user=lightning.host,
                type='번개모임',
                event=lightning,
                message=f"{user.nickname} has canceled their participation in the lightning event [{lightning.title}]."
            )

            # 푸시 알림 전송: 호스트에게
            if lightning.host.fcm_token:
                send_fcm_notification(
                    user=lightning.host,
                    token=lightning.host.fcm_token,
                    title="Leave Meetup",
                    body=f"{user.nickname} has canceled their participation in the lightning event [{lightning.title}]."
                )

        participants = lightning.participants.all()
        serialized_participants = ParticipantSerializer(participants, many=True).data

        return Response({
            "message": "Your participation has been canceled.",
            "participants": serialized_participants
            }, status=200)

# 로그인한 사용자의 Current View
class CurrentLightningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lightnings = Lightning.objects.filter(
            Q(host=user) | Q(participants=user)
        ).distinct()
        serializer = LightningSerializer(lightnings, many=True)
        return Response(serializer.data)


class HostedLightningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lightnings = Lightning.objects.filter(host=user)
        serializer = LightningSerializer(lightnings, many=True)
        return Response(serializer.data)


class ParticipatedLightningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lightnings = Lightning.objects.filter(
            participants=user,  # ManyToManyField 연결 필드
        ).exclude(host=user)  # host는 제외
        serializer = LightningSerializer(lightnings, many=True)
        return Response(serializer.data)
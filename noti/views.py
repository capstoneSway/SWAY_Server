from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User
from noti.fcm import send_fcm_notification

# 알림 전체 목록 조회 (로그인한 사용자의 알림만)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

# 알림 읽음 처리 API (개별 알림 ID로 처리)
class MarkNotificationAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        if notification.is_read:
            return Response({"message": "이미 읽은 알림입니다."})
        
        notification.is_read = True
        notification.save()
        return Response({"message": "알림이 읽음 처리되었습니다."})
    
# 전체 알림 읽음 처리
class MarkAllNotificationsAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_notifications = Notification.objects.filter(user=request.user, is_read=False)
        updated_count = user_notifications.update(is_read=True)
        return Response({
            "message": f"{updated_count}개의 알림을 읽음 처리했습니다."
        })
    
# 읽지 않은 알림 수 조회
class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": unread_count})
    
# 알림 1개 삭제하기
class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        return Response({"message": "알림이 삭제되었습니다."})

# 전체 알림 삭제하기
class DeleteAllNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        deleted_count, _ = Notification.objects.filter(user=request.user).delete()
        return Response({"message": f"총 {deleted_count}개의 알림이 삭제되었습니다."})


class PushTestView(APIView):
    def post(self, request):
        # 요청에서 user_id 가져오기
        user_id = request.data.get('user_id')
        
        # user_id로 User 객체 가져오기
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        
        # FCM 토큰이 없는 경우 처리
        if not user.fcm_token:
            return Response({"error": "FCM 토큰이 없습니다."}, status=400)

        # 이미지 URL을 데이터로 받을 수 있도록 처리
        image_url = request.data.get('image_url', None)  # 이미지 URL을 받음
        
        # FCM 푸시 알림 전송
        send_fcm_notification(
            token=user.fcm_token,
            title="테스트 알림",
            body="테스트 푸시입니다",
            image_url=image_url,  # 이미지 URL을 전달
            user=user
        )

        return Response({"message": "푸시 전송 성공!"})
    
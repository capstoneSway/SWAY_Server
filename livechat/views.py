from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import LiveChatRoom, LiveChatMessage
from .serializers import LiveChatMessageSerializer
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from lightning.models import Lightning
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
class MessageListView(generics.ListAPIView):
    serializer_class = LiveChatMessageSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return LiveChatMessage.objects.filter(room__id=room_id).order_by('created_at')

def chat_room_view(request, lightning_id):
    lightning = get_object_or_404(Lightning, id=lightning_id)
    return render(request, 'livechat/chat_room.html', {'lightning': lightning})

class ChatImageUploadView(APIView):
    permission_classes = [AllowAny,] # ✅ 테스트 중에는 모든 사용자 허용
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, room_id):
        room = get_object_or_404(LiveChatRoom, lightning_id=room_id)
        image = request.FILES.get('image')

        if not image:
            return Response({'error': 'No image provided'}, status=400)
        
        # ✅ 테스트 중에는 강제 유저 지정
        test_user = User.objects.get(email="test@test.com")

        # 메시지 저장
        chat_message = LiveChatMessage.objects.create(
            room=room,
            # sender=request.user,
            sender=test_user, # ✅ 테스트 유저
            picture=image
        )

        # CloudFront 기반 URL 반환
        image_url = f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{chat_message.picture.name}"
        return Response({'image_url': image_url})

class LeaveChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        user = request.user
        room = get_object_or_404(LiveChatRoom, lightning_id=room_id)
        lightning_event = room.lightning

        if not lightning_event:
            return Response({'error': 'Lightning event not found'}, status=404)
        
        if user not in lightning_event.participants.all():
            return Response({'error': 'User is not a participant'}, status=403)
        
        if lightning_event.host == user:
            return Response({'detail': '호스트는 모임에서 나갈 수 없습니다.'}, status=403)
        
        lightning_event.participants.remove(user)
        return Response({'detail': 'You successfully left chat and meetup.'})
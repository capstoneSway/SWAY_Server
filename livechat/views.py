from django.shortcuts import render
from rest_framework import generics, permissions
from .models import LiveChatMessage
from .serializers import LiveChatMessageSerializer
from django.shortcuts import render, get_object_or_404
from lightning.models import Lightning

# Create your views here.
class MessageListView(generics.ListAPIView):
    serializer_class = LiveChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return LiveChatMessage.objects.filter(room__id=room_id).order_by('created_at')

def chat_room_view(request, lightning_id):
    lightning = get_object_or_404(Lightning, id=lightning_id)
    return render(request, 'livechat/chat_room.html', {'lightning': lightning})
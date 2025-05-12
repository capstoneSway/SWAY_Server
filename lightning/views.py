from rest_framework import generics, permissions
from .models import Lightning
from .serializers import LightningSerializer
from rest_framework.exceptions import PermissionDenied


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
        serializer.save(host=self.request.user)  # 주최자는 현재 로그인한 유저

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
        instance.delete()
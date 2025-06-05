from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from mypage.models import BlockUser
from mypage.utils import get_active_restriction
from django.shortcuts import get_object_or_404
from noti.models import Notification
from noti.fcm import send_fcm_notification
from rest_framework import filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework.response import Response

#댓글 알림 함수
def notify_on_comment_create(comment):
    author = comment.user
    board = comment.board
    board_owner = board.user
    parent_comment = comment.parent
    parent_comment_user = parent_comment.user if parent_comment else None

    board_title = board.title[:30]
    comment_preview = comment.content[:50]

    # 게시글 작성자 알림
    if board_owner and board_owner != author:
        message = f"{author.nickname} ({author.username}) commented on your post \"{board_title}\": \"{comment_preview}\""
        Notification.objects.create(
            user=board_owner,
            type='board',
            board=board,
            message=message
        )
        send_fcm_notification(
            user=board_owner,
            title="New Comment",
            body=message,
            data={
                "type": "comment",
                "board_id": str(board.id),
                "comment_id": str(comment.id),
                "content": comment_preview,
                "username": author.username
            }
        )

    # 부모 댓글 작성자 알림 (대댓글)
    if parent_comment and parent_comment_user and parent_comment_user != author:
        parent_preview = parent_comment.content[:50]
        message = f"{author.nickname} ({author.username}) replied to your comment \"{parent_preview}\" on \"{board_title}\""
        Notification.objects.create(
            user=parent_comment_user,
            type='comment',
            board=board,
            message=message
        )
        send_fcm_notification(
            user=parent_comment_user,
            title="New Reply",
            body=message,
            data={
                "type": "reply",
                "board_id": str(board.id),
                "comment_id": str(comment.id),
                "content": parent_preview,
                "username": author.username
            }
        )

class BoardList(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [AllowAny]
    #검색기능
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
	
    def get_queryset(self):
        queryset = Board.objects.all()

        user = self.request.user
        if user.is_authenticated:
            blocked_user_ids = BlockUser.objects.filter(user=user).values_list('blocked_user', flat=True)
            queryset = queryset.exclude(user__in=blocked_user_ids)

        return queryset

class BoardCreate(CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # ✅ 글쓰기 제한 확인
        restriction = get_active_restriction(self.request.user, 'board_ban')
        if restriction:
            if restriction.release_at:
                until = restriction.release_at.strftime('%Y-%m-%d %H:%M')
                msg = f"You are restricted from creating posts until {until}."
            else:
                msg = "You are permanently restricted from creating posts."
            raise PermissionDenied(msg)
        # ✅ 게시글 저장
        board = serializer.save(user=self.request.user)
        # ✅ 이미지 저장
        images = self.request.FILES.getlist('images')
        for image in images:
            BoardImage.objects.create(board=board, image=image)

class BoardDetail(RetrieveDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        # S3에 연결된 이미지도 삭제
        for image in instance.images.all():
            image.delete()
        instance.delete()

class BoardUpdate(RetrieveUpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self):
        board_id = self.kwargs['board_id']
        return get_object_or_404(Board, pk=board_id)

class CommentList(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        board_id = self.kwargs['board_id']
        return Comment.objects.filter(board_id=board_id, parent=None)

    def perform_create(self, serializer):
        restriction = get_active_restriction(self.request.user, 'board_ban')
        if restriction:
            if restriction.release_at:
                until = restriction.release_at.strftime('%Y-%m-%d %H:%M')
                msg = f"You are restricted from posting comments until {until}."
            else:
                msg = "You are permanently restricted from posting comments."
            raise PermissionDenied(msg)
        
        board_id = self.kwargs['board_id']
        board = Board.objects.get(pk=board_id)
        parent_id = self.request.data.get('parent_id')
        parent = get_object_or_404(Comment, pk=parent_id) if parent_id else None
        parent_user = parent.user if parent else None
        comment = serializer.save(user=self.request.user, board=board, parent=parent, parent_user=parent_user)
        notify_on_comment_create(comment)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
        
    
class CommentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['GET', 'PUT', 'PATCH']:
            return CommentDetailSerializer
        return CommentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.is_deleted:
            return Response({"detail": "This comment has already been deleted."}, status=status.HTTP_400_BAD_REQUEST)

        # 소프트 삭제 처리
        instance.content = "[This comment has been deleted.]"
        instance.is_deleted = True
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)



class BoardLikeToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        if board.user == request.user:
            return Response({'error': 'You cannot like your own post.'}, status=400)
        like, created = BoardLike.objects.get_or_create(user=request.user, board=board)
        if not created:
            like.delete()
            return Response({'liked': False})
        return Response({'liked': True})

    def delete(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        BoardLike.objects.filter(user=request.user, board=board).delete()
        return Response({'liked': False})

    
class CommentLikeToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id, board_id=board_id)
        if comment.user == request.user:
            return Response({'error': 'You cannot like your own comment.'}, status=400)

        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        liked = created  # True if newly liked

        # ✅ 개선된 응답: 댓글 정보 통째로 반환
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, board_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id, board_id=board_id)
        CommentLike.objects.filter(user=request.user, comment=comment).delete()

        # ✅ 삭제 후에도 최신 상태 응답
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)

    
class BoardScrapToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        if board.user == request.user:
            return Response({'error': 'You cannot scrap your own post.'}, status=400)

        scrap, created = BoardScrap.objects.get_or_create(user=request.user, board=board)
        if not created:
            scrap.delete()
            return Response({'scrapped': False})
        return Response({'scrapped': True})

    def delete(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        BoardScrap.objects.filter(user=request.user, board=board).delete()
        return Response({'scrapped': False})


class BoardNotiToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        noti, created = Boardnoti.objects.get_or_create(user=request.user, board=board)
        serializer = BoardSerializer(board, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        Boardnoti.objects.filter(user=request.user, board=board).delete()
        serializer = BoardSerializer(board, context={'request': request})
        return Response(serializer.data)
    
class CommentNotiToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        noti, created = Commentnoti.objects.get_or_create(user=request.user, comment=comment)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        Commentnoti.objects.filter(user=request.user, comment=comment).delete()
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)
    
class BoardReportView(CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        board_id = self.kwargs['board_id']
        board = get_object_or_404(Board, pk=board_id)
        serializer.save(reporter=self.request.user, board=board)

class CommentReportView(CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        comment_id = self.kwargs['comment_id']
        comment = get_object_or_404(Comment, pk=comment_id)
        serializer.save(reporter=self.request.user, comment=comment)

class AddBlockUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        blocker = request.user
        blocked = board.user

        if blocker == blocked:
            return Response({'detail': 'You cannot block yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if BlockUser.objects.filter(user=blocker, blocked_user=blocked).exists():
            return Response({'detail': 'This user is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

        BlockUser.objects.create(user=blocker, blocked_user=blocked)
        return Response({'detail': f'{blocked.nickname} has been blocked successfully.'}, status=status.HTTP_201_CREATED)

class AddBlockCommentUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        blocker = request.user
        blocked = comment.user

        if blocker == blocked:
            return Response({'detail': 'You cannot block yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if BlockUser.objects.filter(user=blocker, blocked_user=blocked).exists():
            return Response({'detail': 'This user is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

        BlockUser.objects.create(user=blocker, blocked_user=blocked)
        return Response({'detail': f'{blocked.nickname} has been blocked successfully.'}, status=status.HTTP_201_CREATED)

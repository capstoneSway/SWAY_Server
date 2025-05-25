from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from mypage.models import BlockUser
from mypage.utils import get_active_restriction
from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework.response import Response



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
        restriction = get_active_restriction(self.request.user, 'board_ban')
        if restriction:
            if restriction.release_at:
                until = restriction.release_at.strftime('%Y-%m-%d %H:%M')
                msg = f"You are restricted from creating posts until {until}."
            else:
                msg = "You are permanently restricted from creating posts."
            raise PermissionDenied(msg)
        serializer.save(user=self.request.user)

class BoardDetail(RetrieveDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrReadOnly]

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

        serializer.save(user=self.request.user, board=board, parent=parent, parent_user=parent_user)
    
class CommentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['GET', 'PUT', 'PATCH']:
            return CommentDetailSerializer
        return CommentSerializer



class BoardLikeToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
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
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            like.delete()
            return Response({'liked': False})
        return Response({'liked': True})

    def delete(self, request, board_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id, board_id=board_id)
        CommentLike.objects.filter(user=request.user, comment=comment).delete()
        return Response({'liked': False})

    
class BoardScrapToggleView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        scrap, created = BoardScrap.objects.get_or_create(user=request.user, board=board)
        if not created:
            scrap.delete()
            return Response({'scrapped': False})
        return Response({'scrapped': True})

    def delete(self, request, board_id):
        board = get_object_or_404(Board, pk=board_id)
        BoardScrap.objects.filter(user=request.user, board=board).delete()
        return Response({'scrapped': False})
    
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

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        blocker = request.user
        blocked = comment.user

        if blocker == blocked:
            return Response({'detail': 'You cannot block yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if BlockUser.objects.filter(user=blocker, blocked_user=blocked).exists():
            return Response({'detail': 'This user is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

        BlockUser.objects.create(user=blocker, blocked_user=blocked)
        return Response({'detail': f'{blocked.nickname} has been blocked successfully.'}, status=status.HTTP_201_CREATED)

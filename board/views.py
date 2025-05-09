from .models import Board, Comment
from .serializers import BoardSerializer, CommentSerializer, CommentDetailSerializer
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

class BoardList(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    #검색기능
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'body']
		
class BoardCreate(CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BoardDetail(RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

class CommentList(ListCreateAPIView):
    #queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        board_id = self.kwargs['board_id']
        return Comment.objects.filter(board_id=board_id, parent=None)

    def perform_create(self, serializer):
        board_id = self.kwargs['board_id']
        board = Board.objects.get(pk=board_id)
        parent_id = self.request.data.get('parent')
        parent = get_object_or_404(Comment, pk=parent_id) if parent_id else None
        parent_user = parent.user if parent else None
        serializer.save(user=self.request.user, board=board, parent=parent, parent_user=parent_user)
    
class CommentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentDetailSerializer
        return CommentSerializer
from .models import *
from .serializers import BoardSerializer, CommentSerializer, CommentDetailSerializer
from rest_framework import filters, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

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

class BoardDetail(RetrieveDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

class BoardUpdate(RetrieveUpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self):
        board_id = self.kwargs['board_id']
        return get_object_or_404(Board, pk=board_id)

class CommentList(ListCreateAPIView):
    #queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        board_id = self.kwargs['board_id']
        return Comment.objects.filter(board_id=board_id, parent_id=None)

    def perform_create(self, serializer):
        board_id = self.kwargs['board_id']
        board = Board.objects.get(pk=board_id)
        parent_id = self.request.data.get('parent_id')
        parent = get_object_or_404(Comment, pk=parent_id) if parent_id else None
        parent_user = parent.user if parent else None
        serializer.save(user=self.request.user, board=board, parent_id=parent, parent_user=parent_user)
    
class CommentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    authentication_classes = [JWTAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
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

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            like.delete()
            return Response({'liked': False})
        return Response({'liked': True})

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
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


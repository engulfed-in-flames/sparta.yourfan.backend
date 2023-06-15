from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from .permissions import IsAdminOrIsUserMatch
from rest_framework.response import Response
from rest_framework import status
from .models import Board, Post, Comment
from .serializers import *


class BoardModelViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        board = get_object_or_404(Board, pk=pk)
        board.is_active = False
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        if "name" in request.data:
            return Response(
                {"message": "게시판 명칭은 임의대로 변경이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)


class PostModelViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return PostSerializer
        print("view")
        return PostNotGetSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [IsAdminOrIsUserMatch]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return CommentSerializer
        return CommentNotGetSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [IsAdminOrIsUserMatch]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

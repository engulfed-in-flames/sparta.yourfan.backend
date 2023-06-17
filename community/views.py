from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action
from yourfan.permissions import  isAdminOrStaffOrMatch,ISNotBannedUser
from rest_framework.response import Response
from rest_framework import status
from .models import Board, Post, Comment
from .serializers import *
from django.contrib.auth import get_user_model

class BoardModelViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = 'name'
    

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
    
    @action(detail=True, methods=["POST"])
    def subscribe(self,request,name=None):
        board = self.get_object()
        board.subscribers.add(request.user)
        
        return Response({"status":"subscribed..."},status=status.HTTP_200_OK)
    
    @action(detail=True,methods=["POST"])
    def ban(self,request,name=None):
        target = get_user_model().objects.get(pk=request.data["user_id"])
        board = self.get_object()

        if board.banned_users.filter(id=target.id).exists(): 
            board.banned_users.remove(target)
            return Response({"status":"ban release completed"},status=status.HTTP_200_OK)
        else:
            board.banned_users.add(target)
            return Response({"status":"ban completed"},status=status.HTTP_200_OK)

        

class PostModelViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return PostSerializer
        return PostNotGetSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [isAdminOrStaffOrMatch]
        else:
            permission_classes = [ISNotBannedUser,IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=["POST "])
    def bookmark(self,request,pk=None):
        post = self.get_object()
        post.bookmarked_by.add(request.user)
        
        return Response({"status":"bookmarked..."},status=status.HTTP_200_OK)


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return CommentSerializer
        return CommentNotGetSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [isAdminOrStaffOrMatch]
        else:
            permission_classes = [ISNotBannedUser,IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
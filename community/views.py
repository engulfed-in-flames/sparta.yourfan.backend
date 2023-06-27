from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action
from yourfan.permissions import  UserMatch,ISNotBannedUser,IsStaff
from rest_framework.response import Response
from rest_framework import status
from .models import Board, Post, Comment
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
import django_filters
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()


class BoardFilter(django_filters.FilterSet):
    rank = django_filters.CharFilter(lookup_expr='icontains')
    title = django_filters.CharFilter(lookup_expr='icontains')
    custom_url = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Board
        fields = ["rank","title","custom_url"]

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains') 

    class Meta:
        model = Post
        fields = ["title","content"]

class CommunityPagination(PageNumberPagination):
    page_size = 15
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page': self.page.number,
            'results': data,
        })


class BoardModelViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all().order_by('-created_at')
    serializer_class = BoardSerializer
    lookup_field = 'custom_url'
    pagination_class = CommunityPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BoardFilter
    
    def get_permissions(self):
        if self.action in ["destroy", "create"]:
            permission_classes = [IsAdminUser]
        elif self.action in ["partial_update","update","ban"]:
            permission_classes = [IsStaff|IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        serializer = BoardCreateSerializer(data=request.data)
        channel = get_object_or_404(Channel, channel_id=request.data['channel_id'])
        if serializer.is_valid():
            serializer.save(channel=channel)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        custom_url = self.kwargs.get("custom_url")
        board = get_object_or_404(Board, custom_url=custom_url)
        board.is_active = False
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        if "title" in request.data:
            return Response(
                {"message": "게시판 명칭은 임의대로 변경이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=["POST"])
    def subscribe(self,request,custom_url=None):
        board = self.get_object()
        
        if board.subscribers.filter(id=request.user.id).exist():
            board.subscribers.remove(request.user)
            return Response({"message":"unsubscribed..."},status=status.HTTP_200_OK)
        else:
            board.subscribers.add(request.user)
            return Response({"message":"subscribed..."},status=status.HTTP_200_OK)
    
    @action(detail=True,methods=["POST"])
    def ban(self,request,custom_url=None):
        target = get_object_or_404(User,pk=request.data["user_id"])
        board = self.get_object()

        if board.banned_users.filter(id=target.id).exists(): 
            board.banned_users.remove(target)
            return Response({"message":"ban release completed"},status=status.HTTP_200_OK)
        else:
            board.banned_users.add(target)
            return Response({"message":"ban completed"},status=status.HTTP_200_OK)

class BoardPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ISNotBannedUser]
    pagination_class = CommunityPagination
    
    def get_queryset(self):
        custom_url = self.kwargs.get('board_custom_url')
        board = get_object_or_404(Board,custom_url=custom_url)
        return Post.objects.filter(board=board).order_by('-created_at')

class PostModelViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    pagination_class = CommunityPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostNotGetSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [UserMatch | IsStaff]
        else:
            permission_classes = [ISNotBannedUser,IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def partial_update(self, request, *args, **kwargs):
        if "board" in request.data:
            return Response(
                {"message": "포스트 수정시 게시판은 임의대로 변경이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)
    
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
            permission_classes = [UserMatch | IsStaff]
        else:
            permission_classes = [ISNotBannedUser,IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def partial_update(self, request, *args, **kwargs):
        if "post" in request.data:
            return Response(
                {"message": "게시글은 임의대로 변경이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)

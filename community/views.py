import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle
from rest_framework import permissions

from yourfan.permissions import UserMatch, ISNotBannedUser, IsStaff
from .models import Board, Post, Comment, StaffConfirm
from .serializers import *


User = get_user_model()


# 커뮤니티 모델을 위한 view들입니다
# 모든 viewset에서 board를 함부로 수정할 수 없도록 되어있습니다.
# 메서드에 따라 serializer를 각각 다르게 불러오도록 설정되어 있습니다.
# get_permission에서 권한 설정을 하신걸 볼 수 있습니다.


# 게시판 검색시 사용되는 필터입니다. 사용법은 url 끝에 ?<필드명>=<검색값>입니다
# ex) GET .../community/board/?custom_url=ABC


class BoardFilter(django_filters.FilterSet):
    rank = django_filters.CharFilter(lookup_expr="icontains")
    title = django_filters.CharFilter(lookup_expr="icontains")
    custom_url = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Board
        fields = ["rank", "title", "custom_url"]


# 게시물 검색시 사용되는 필터입니다. 사용법은 url 끝에 ?<필드명>=<검색값>입니다
# ex) GET .../community/post/?title=ABC


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    content = django_filters.CharFilter(lookup_expr="icontains")
    user__nickname = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Post
        fields = ["title", "content", "user__nickname"]


# 페이지네이션 설정 클래스입니다.
# page_size를 통해 한 페이지에 들어갈 인스턴스 갯수를 제한할 수 있습니다.
# return 내부를 조정하여 반환되는 형태를 조정할 수 있습니다


class CommunityPagination(PageNumberPagination):
    page_size = 15
    page_query_param = "page"

    def get_paginated_response(self, data):
        result_data = []
        start_index = self.page.start_index()
        total_index = self.page.paginator.count
        for index, item in enumerate(data, start=start_index):
            item["post_no"] = total_index - index + 1
            result_data.append(item)

        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "page": self.page.number,
                "results": result_data,
            }
        )


# 게시판 모델 Board의 viewset입니다.
# lookup_field로 인해 pk는 custom_url 입니다.
# 스태프 이상만 가능한 ban 메서드는 user의 pk를 전송하면 해당 user를 banned_user 필드에 추가합니다.
# subscribe는 해당 게시판을 즐겨찾기 하기 위한 메서드입니다.


class BoardModelViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = "custom_url"
    filter_backends = [DjangoFilterBackend]
    filterset_class = BoardFilter

    def get_permissions(self):
        if self.action in ["destroy", "create"]:
            permission_classes = [IsAdminUser]
        elif self.action in ["partial_update", "update", "ban"]:
            permission_classes = [IsStaff | IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = BoardCreateSerializer(data=request.data)
        channel = get_object_or_404(Channel, channel_id=request.data["channel_id"])
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
    def subscribe(self, request, custom_url=None):
        board = self.get_object()

        if board.subscribers.filter(id=request.user.id).exists():
            board.subscribers.remove(request.user)
            return Response(status=status.HTTP_200_OK)
        else:
            board.subscribers.add(request.user)
            return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def ban(self, request, custom_url=None):
        target = get_object_or_404(User, pk=request.data["user_id"])
        board = self.get_object()

        if board.banned_users.filter(id=target.id).exists():
            board.banned_users.remove(target)
            return Response(status=status.HTTP_200_OK)
        else:
            board.banned_users.add(target)
            return Response(status=status.HTTP_200_OK)


# 특정 게시판의 Post들을 일괄적으로 출력(List,Retrieve)하기 위한 뷰셋입니다.


class BoardPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ISNotBannedUser]
    pagination_class = CommunityPagination

    def get_queryset(self):
        custom_url = self.kwargs.get("board_custom_url")
        board = get_object_or_404(Board, custom_url=custom_url)
        return Post.objects.filter(board=board).order_by("-created_at")


class UserPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(user=user).order_by("-created_at")

class SubscriberViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BoardSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(subscribers=user)

# 포스트 모델을 위한 viewset입니다.
# 기본적인 쿼리는 작성일 역순입니다. django-filter를 이용한 검색이 가능하며 페이지네이션 되고 있습니다.
# 북마크 메서드 역시 존재하며 작동원리는 book_marked 필드에 user를 추가하는 것입니다.
# update는 유저 자신만이 가능하며, destroy는 admin,staff,유저 자신만 가능합니다.
# banned_user는 GET 요청만이 가능하며 그외의 작동은 403을 띄우도록 되어있습니다.


class PostModelViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
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
        if self.action in ["update", "partial_update"]:
            permission_classes = [UserMatch]
        elif self.action in ["destroy"]:
            permission_classes = [UserMatch | IsStaff]
        else:
            permission_classes = [ISNotBannedUser, IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        if "board" in request.data:
            return Response(
                {"message": "포스트 수정시 게시판은 임의대로 변경이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["POST "])
    def bookmark(self, request, pk=None):
        post = self.get_object()
        post.bookmarked_by.add(request.user)

        return Response({"status": "bookmarked..."}, status=status.HTTP_200_OK)


# 코멘트 모델을 위한 viewset입니다. 포스트 viewset과 거의 동일합니다.


class CommentModelViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return CommentSerializer
        return CommentNotGetSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [UserMatch]
        elif self.action in ["destroy"]:
            permission_classes = [UserMatch | IsStaff]
        else:
            permission_classes = [ISNotBannedUser, IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        if "post" in request.data:
            return Response(
                {"message": "게시글은 임의대로 변경이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)


# 스태프 신청과 완료를 위한 뷰셋입니다.
# 사용될 actions는 List, Retrieve, Create, Update 입니다.
# List(GET),Retrieve(GET) 으로 신청 대기중인(status="P") staffConfirm 모델 인스턴스들을 확인합니다
# Create(Post)는 유저가 사용하는 메서드입니다.JSON에 보드 custom_url만 담으면 됩니다.
# admin user가 update를 status를 A(accept)로 업데이트 하는 순간, user의 staff가 변경됩니다.
# 그렇기에 권한은 create만 밴된 유저를 제외하고 가능하게 했고, 그 외에는 admin user만 가능합니다.
# 쿼리셋은 status = P인 인스턴스만 보여집니다. 따라서 변경이 완료된 이후로는 보이지 않게 됩니다.


class StaffConfirmViewSet(viewsets.ModelViewSet):
    serializer_class = StaffConfirmSerializer

    def get_queryset(self):
        return StaffConfirm.objects.filter(status="P")

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [ISNotBannedUser]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        user_try = StaffConfirm.objects.filter(board__custom_url=request.data.get("board"),user=request.user)
    
        if user_try.exists():
            user_try = user_try.first()
            if user_try.status == "A":
                return Response({"message":"이미 관리자입니다."},status=status.HTTP_401_UNAUTHORIZED)
            elif user_try.status == "P":
                return Response({"message":"아직 admin이 허가하지 않았습니다."},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message":"거절되었습니다."},status=status.HTTP_401_UNAUTHORIZED)
        
        return super().create(request, *args, **kwargs)
            

    def partial_update(self, request, *args, **kwargs):
        staff_confirm = self.get_object()
        confirm_status = request.data.get("status")

        if confirm_status == "A":
            board = staff_confirm.board
            user = staff_confirm.user
            board.staffs.add(user)
            staff_confirm.status = confirm_status
            staff_confirm.save(update_fields=["status"])
        
        elif confirm_status == "R":
            staff_confirm.status = confirm_status
            staff_confirm.save(update_fields=["status"])

        serializer = self.get_serializer(staff_confirm)
        return Response(serializer.data, status=status.HTTP_200_OK)

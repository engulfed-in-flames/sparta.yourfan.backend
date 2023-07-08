from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BoardModelViewSet,
    PostModelViewSet,
    CommentModelViewSet,
    BoardPostViewSet,
    StaffConfirmViewSet,
    UserPostViewSet,
    SubscriberViewSet
)

router = DefaultRouter()
router.register(
    "board",
    BoardModelViewSet,
    basename="board",
)
router.register(
    "post",
    PostModelViewSet,
    basename="post",
)
router.register(
    "comment",
    CommentModelViewSet,
    basename="comment",
)

router.register(
    r"board/(?P<board_custom_url>.+)/posts",
    BoardPostViewSet,
    basename="board_posts",
)

router.register(
    r"user",
    UserPostViewSet,
    basename="user_posts",
)

router.register(
    r"subscribe",
    SubscriberViewSet,
    basename="subscribe",
)


router.register("staff", StaffConfirmViewSet, basename="staff")

urlpatterns = [path("", include(router.urls))]

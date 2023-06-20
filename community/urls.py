from rest_framework.routers import DefaultRouter
from .views import BoardModelViewSet, PostModelViewSet, CommentModelViewSet, BoardPostViewSet
from django.urls import path, include

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
    r'board/(?P<board_name>.+)/posts',
    BoardPostViewSet,
    basename="board_posts",
)

urlpatterns = [path("", include(router.urls))]

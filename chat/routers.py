from rest_framework.routers import DefaultRouter
from chat.views import ChatroomViewSet,MessageViewSet

router = DefaultRouter()
router.register('rooms',ChatroomViewSet,basename='room')
router.register('messages',MessageViewSet,basename='message')

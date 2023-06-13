from rest_framework.routers import DefaultRouter
from .views import ChatroomViewSet,MessageViewSet
from django.urls import path,include

router = DefaultRouter()
router.register('rooms',ChatroomViewSet,basename='room')
router.register('messages',MessageViewSet,basename='message')

urlpatterns = [
    path('',include(router.urls))
]

from rest_framework.routers import DefaultRouter
from .views import ChatroomViewSet
from django.urls import path,include

router = DefaultRouter()
router.register('rooms',ChatroomViewSet,basename='room')

urlpatterns = [
    path('',include(router.urls))
]

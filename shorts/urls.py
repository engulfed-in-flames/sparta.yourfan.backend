from rest_framework.routers import DefaultRouter
from .views import ShortModelViewset
from django.urls import path,include

router = DefaultRouter()
router.register('',ShortModelViewset,basename='shorts')

urlpatterns = [
    path('',include(router.urls))
]

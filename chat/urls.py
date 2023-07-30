from django.urls import path,include
from chat.routers import router

urlpatterns = [
    path('',include(router.urls))
]

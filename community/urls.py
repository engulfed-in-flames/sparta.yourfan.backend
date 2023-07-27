from django.urls import path, include
from community.routers import router

urlpatterns = [path("", include(router.urls))]

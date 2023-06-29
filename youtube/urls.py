from django.urls import path
from . import views

urlpatterns = [
    path(
        "find/<str:channel>/",
        views.FindChannel.as_view(),
        name="find_channel",
    ),
    path(
        "<str:channel_id>/",
        views.ChannelModelView.as_view(),
        name="channel",
    ),
    path(
        "detail/<str:custom_url>/",
        views.ChannelDetailView.as_view(),
        name="channel_detail",
    ),
]

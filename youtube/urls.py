from django.urls import path,re_path

from . import views

urlpatterns = [
    path('find/<str:title>/', views.FindChannel.as_view(), name='find_channel'),
    path('', views.ChannelModelView.as_view(), name='channel'),
    path('detail/', views.ChannelDetailView.as_view(), name='channel_detail'),
]

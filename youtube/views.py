from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from community.serializers import BoardCreateSerializer
from .models import Channel, ChannelDetail
from . import serializers
from . import youtube_api
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
import datetime
import logging

logging.basicConfig(filename='error.log', level=logging.ERROR)

class FindChannel(APIView):
    # permission_classes = [IsAuthenticated]
    """
    채널 조회\
    검색결과 중 상위 5개를 딕셔너리를 포함한 리스트로 출력
    """

    def post(self, request, channel):
        youtube = youtube_api.youtube
        try:
            channels = youtube_api.find_channelid(youtube, channel)
        except:
            Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(channels, status=status.HTTP_200_OK)


class ChannelModelView(APIView):
    def get(self, request, channel_id):
        try:
            channel = Channel.objects.get(channel_id=channel_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, channel_id):
        youtube = youtube_api.youtube
        channel = Channel.objects.filter(channel_id=channel_id).exists()
        if channel:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            channel_data = youtube_api.get_channel_stat(youtube, channel_id)
            if not "upload_list" in channel_data:
                return Response(status=status.HTTP_410_GONE)
            if int(channel_data["subscriber"]) < 10000:
                return Response(status=status.HTTP_423_LOCKED)
            with transaction.atomic():
                serializer = serializers.CreateChannelSerializer(data=channel_data)
                if serializer.is_valid():
                    channel = serializer.save()
                    channel_detail_data = youtube_api.get_latest30_video_details(
                        youtube, channel_data
                    )
                    channel_data.update(channel_detail_data)
                    channel_heatmap_url = youtube_api.create_channel_heatmap_url(
                        channel_data
                    )
                    channel_data["channel_activity"] = channel_heatmap_url
                    wordcloud_url = youtube_api.create_wordcloud_url(channel_data)
                    channel_data["channel_wordcloud"] = wordcloud_url
                    detail_serializer = serializers.CreateChannelDetailSerializer(
                        data=channel_data
                    )
                    if detail_serializer.is_valid():
                        detail_serializer.save(channel=channel)
                    else:
                        raise Exception("error")
                    board_serializer = BoardCreateSerializer(data=channel_data)
                    if board_serializer.is_valid():
                        board_serializer.save(channel=channel)
                        return Response(status=status.HTTP_201_CREATED)
                    else:
                        raise Exception("error")
                else:
                    raise Exception("error")
        except :
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, channel_id):
        channel = get_object_or_404(Channel, channel_id=channel_id)
        youtube = youtube_api.youtube
        try:
            channel_data = youtube_api.get_channel_stat(youtube, channel_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.ChannelSerializer(
            instance=channel, data=channel_data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, channel_id):
        channel = get_object_or_404(Channel, channel_id=channel_id)
        channel.delete()
        return Response(status=status.HTTP_200_OK)


class ChannelDetailView(APIView):
    def get(self, request, custom_url):
        channel = get_object_or_404(Channel, custom_url=custom_url)
        detail = (
            ChannelDetail.objects.filter(channel=channel.pk)
            .order_by("-updated_at")
            .first()
        )
        serializer = serializers.ChannelDetailSerializer(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, custom_url):
        youtube = youtube_api.youtube
        channel = get_object_or_404(Channel, custom_url=custom_url)
        try:
            with transaction.atomic():
                try:
                    channel_data = youtube_api.get_channel_stat(
                        youtube, channel.channel_id
                    )
                    channel_detail_data = youtube_api.get_latest30_video_details(
                        youtube, channel_data
                    )
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                channel_data.update(channel_detail_data)
                channel_heatmap_url = youtube_api.create_channel_heatmap_url(
                    channel_data
                )
                channel_data["channel_activity"] = channel_heatmap_url
                wordcloud_url = youtube_api.create_wordcloud_url(channel_data)
                channel_data["channel_wordcloud"] = wordcloud_url
                detail_serializer = serializers.CreateChannelDetailSerializer(
                    data=channel_data
                )
                if detail_serializer.is_valid():
                    detail_serializer.save(channel=channel)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(
                        detail_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

def update_data():
    youtube = youtube_api.youtube
    channels = Channel.objects.all()
    for channel in channels:
        try:
            with transaction.atomic():
                try:
                    channel_data = youtube_api.get_channel_stat(
                        youtube, channel.channel_id
                    )
                    channel_detail_data = youtube_api.get_latest30_video_details(
                        youtube, channel_data
                    )
                except:
                    raise Exception("data를 불러오지 못했습니다")
                channel_data.update(channel_detail_data)
                channel_heatmap_url = youtube_api.create_channel_heatmap_url(
                    channel_data
                )
                channel_data["channel_activity"] = channel_heatmap_url
                wordcloud_url = youtube_api.create_wordcloud_url(channel_data)
                channel_data["channel_wordcloud"] = wordcloud_url
                detail_serializer = serializers.CreateChannelDetailSerializer(
                    data=channel_data
                )
                if detail_serializer.is_valid():
                    detail_serializer.save(channel=channel)
                else: 
                    raise Exception(detail_serializer.errors)
        except Exception as e:
            logging.exception(channel.title, channel.channel_id, e)
 

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Channel, ChannelDetail
from community.serializers import BoardSerializer, BoardCreateSerializer
from . import serializers
from . import youtube_api


class FindChannel(APIView):
    """
    채널 조회

    검색결과 중 상위 5개를 딕셔너리를 포함한 리스트로 출력

    data = [{
        "channel_name",
        "channel_id",
        "subscriber",
        "thumbnail"
    },...]
    """

    def post(self, request, title):
        youtube = youtube_api.youtube
        channels = youtube_api.find_channelid(youtube, title)
        return Response(channels, status=status.HTTP_200_OK)


class ChannelModelView(APIView):
    def get(self, request):
        channel_id = request.data.get("channel_id")
        channel = Channel.objects.get(channel_id=channel_id)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        channel_id = request.data.get("channel_id")
        print(channel_id)
        youtube = youtube_api.youtube
        try:
            channel = Channel.objects.get(channel_id=channel_id)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Channel.DoesNotExist:
            channel_data = youtube_api.get_channel_stat(youtube, channel_id)

            topic = youtube_api.topic_id_dict
            channel_data["topic_id"] = []
            if channel_data["topic_ids"]:
                for i in channel_data["topic_ids"]:
                    channel_data["topic_id"].append(topic[i])

            serializer = serializers.CreateChannelSerializer(data=channel_data)
            if serializer.is_valid():
                channel = serializer.save()
                detail_serializer = serializers.CreateChannelDetailSerializer(
                    data=channel_data
                )
                if detail_serializer.is_valid():
                    detail_serializer.save(channel=channel)
                else:
                    return Response(
                        {"channel_detail_error": detail_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                board_serializer = BoardCreateSerializer(data=channel_data)
                if board_serializer.is_valid():
                    board_serializer.save(channel=channel)
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {"board_error": board_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"channel_error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    def put(self, request):
        channel_id = request.data.get("channel_id")
        channel = Channel.objects.get(channel_id=channel_id)
        youtube = youtube_api.youtube
        channel_data = youtube_api.get_channel_stat(youtube, channel_id)
        topic = youtube_api.topic_id_dict
        channel_data["channel_id"] = channel_id
        channel_data["topic_id"] = []
        if channel_data["topic_ids"]:
            for i in channel_data["topic_ids"]:
                channel_data["topic_id"].append(topic[i])
        serializer = serializers.ChannelSerializer(
            instance=channel, data=channel_data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        channel_id = request.data.get("channel_id")
        channel = get_object_or_404(Channel, channel_id=channel_id)
        channel.delete()
        return Response(status=status.HTTP_200_OK)


class ChannelDetailView(APIView):
    def get(self, request):
        channel_id = request.data.get("channel_id")

        channel = Channel.objects.get(channel_id=channel_id)
        detail = ChannelDetail.objects.filter(channel=channel.pk)
        serializer = serializers.ChannelDetailSerializer(detail, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        channel_id = request.data.get("channel_id")

        youtube = youtube_api.youtube
        channel = Channel.objects.get(channel_id=channel_id)
        channel_data = youtube_api.get_channel_stat(youtube, channel_id)
        serializer = serializers.CreateChannelDetailSerializer(data=channel_data)
        if serializer.is_valid():
            serializer.save(channel=channel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        channel_id = request.data.get("channel_id")
        youtube = youtube_api.youtube
        response = youtube_api.get_channel_comment(youtube, channel_id)
        return Response(response, status=status.HTTP_200_OK)

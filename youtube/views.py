from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Channel, ChannelDetail
from . import serializers
from . import youtube_api

class FindChannel(APIView):
    '''
    채널 조회

    검색결과 중 상위 5개를 딕셔너리를 포함한 리스트로 출력

    data = [{
        "channel_name",
        "channel_id",
        "subscriber",
        "thumbnail"
    },...]
    '''
    def get(self, request):
        youtube = youtube_api.youtube
        title = request.GET.get('title')
        if title is None:
            return Response({'message':'채널 아이디를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
        channels = youtube_api.find_channelid(youtube,title)
        return Response(channels, status=status.HTTP_200_OK)
    

class ChannelModelView(APIView):
    def get(self, request, channel_id):
        channel = Channel.objects.get(channel_id=channel_id)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    def post(self, request, channel_id):
        youtube = youtube_api.youtube
        if Channel.objects.get(channel_id=channel_id):
            return Response({'message':'이미 존재하는 채널입니다'})
        channel_data = youtube_api.get_channel_stat(youtube, channel_id)
        if channel_data=='error':
            return Response({'message':'존재하지 않는 채널입니다'})
        topic = youtube_api.topic_id_dict
        channel_data['channel_id']=channel_id
        channel_data['topic_id']=[]
        if channel_data['topic_ids']:
            for i in channel_data['topic_ids']:
                channel_data['topic_id'].append(topic[i])

        serializer = serializers.CreateChannelSerializer(data=channel_data)
        if serializer.is_valid():
            channel=serializer.save()
            detail_serializer = serializers.CreateChannelDetailSerializer(data=channel_data)
            if detail_serializer.is_valid():
                detail_serializer.save(channel=channel)
                return Response({'channel_data':serializer.data,'channel_detail_data':detail_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'channel_detail_error':detail_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'channel_error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, channel_id):
        channel = Channel.objects.get(channel_id=channel_id)
        youtube = youtube_api.youtube
        channel_data = youtube_api.get_channel_stat(youtube, channel_id)
        topic = youtube_api.topic_id_dict
        channel_data['channel_id']=channel_id
        channel_data['topic_id']=[]
        if channel_data['topic_ids']:
            for i in channel_data['topic_ids']:
                channel_data['topic_id'].append(topic[i])
        serializer = serializers.ChannelSerializer(instance=channel, data=channel_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, channel_id):
        channel = get_object_or_404(Channel,channel_id=channel_id)
        channel.delete()
        return Response({'message':'채널 삭제 완료'}, status=status.HTTP_200_OK)


class ChannelDetailView(APIView):
    def get(self, request, channel_id):
        channel = Channel.objects.get(channel_id=channel_id)
        detail = ChannelDetail.objects.filter(channel=channel.pk)
        serializer = serializers.ChannelDetailSerializer(detail, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, channel_id):
        youtube = youtube_api.youtube
        channel = Channel.objects.get(channel_id=channel_id)
        channel_data = youtube_api.get_channel_stat(youtube, channel_id)
        serializer = serializers.CreateChannelDetailSerializer(data=channel_data)
        if serializer.is_valid():
            serializer.save(channel=channel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





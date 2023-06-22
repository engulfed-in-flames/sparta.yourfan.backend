from rest_framework.serializers import ModelSerializer
from .models import Channel, ChannelDetail
from .youtube_api import id_topic_dict

class CreateChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = ("channel_id","title","description","custom_url","published_at","thumbnail","topic_id","keyword","banner","upload_list")


class CreateChannelDetailSerializer(ModelSerializer):
    class Meta:
        model = ChannelDetail
        fields = ("total_view","subscriber","video_count","latest25_views","latest25_likes","latest25_comments")

    # channel_title 필드 추가
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['channel_title'] = instance.channel.title
        return representation

class ChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"

    # topic_id 필드의 출력 변경(pk > topic)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        topic=[id_topic_dict[id] for id in representation['topic_id']]
        representation['topic_id'] = ' '.join(topic)
        return representation


class ChannelDetailSerializer(ModelSerializer):
    class Meta:
        model = ChannelDetail
        fields = "__all__"


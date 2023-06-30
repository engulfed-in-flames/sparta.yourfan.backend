from rest_framework.serializers import ModelSerializer
from .models import Channel, ChannelDetail
from .youtube_api import id_topic_dict


class CreateChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            "channel_id",
            "title",
            "description",
            "custom_url",
            "published_at",
            "thumbnail",
            "topic_id",
            "keyword",
            "banner",
            "upload_list",
        )


class CreateChannelDetailSerializer(ModelSerializer):
    class Meta:
        model = ChannelDetail
        fields = [
            "total_view",
            "subscriber",
            "video_count",
            "latest30_views",
            "latest30_likes",
            "latest30_comments",
            "rank",
            "participation_rate",
            "activity_rate",
            "avg_views",
            "avg_likes",
            "avg_comments",
            "like_per_view",
            "comment_per_view",
            "channel_activity",
            "channel_wordcloud",
        ]

    # channel_title 필드 추가
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["channel_title"] = instance.channel.title
        return representation


class ChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"

    # topic_id 필드의 출력 변경(pk > topic)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        topic = [id_topic_dict[id] for id in representation["topic_id"]]
        representation["topic_id"] = ", ".join(topic)
        return representation


class ChannelDetailSerializer(ModelSerializer):
    class Meta:
        model = ChannelDetail
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        channel = Channel.objects.get(pk=representation['channel'])
        representation["topic_id"] = [id_topic_dict[topic.id] for topic in channel.topic_id.all()]
        representation["title"] = channel.title
        for key,value in representation.items():
            if value in [0,"0",""] and key != "channel_wordcloud":
                representation[key] = "정보가 없습니다"
        return representation
    

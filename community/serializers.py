from rest_framework import serializers
from .models import Board, Post, Comment
from users.serializers import UserSerializer
from youtube.models import Channel, ChannelDetail


class BoardSerializer(serializers.ModelSerializer):
    subscriber_count = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "pk",
            "title",
            "custom_url",
            "channel",
            "channel_id",
            "rank",
            "is_active",
            "subscriber_count",
            "banned_users",
        ]

    def get_subscriber_count(self, obj):
        return obj.subscribers.count()

    def get_title(self, obj):
        return obj.channel.title


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = [
            "board_channel_id",
            "rank",
            "is_active",
        ]

    def to_internal_value(self, data):
        if data.get("channel_id"):
            channel_id = data.get("channel_id")
            channel = Channel.objects.get(channel_id=channel_id)
            channel_detail = ChannelDetail.objects.get(channel=channel.pk)
            subscribers_count = channel_detail.subscriber

            if subscribers_count >= 10000000:
                rank = "diamond"
            elif subscribers_count >= 1000000:
                rank = "gold"
            elif subscribers_count >= 100000:
                rank = "silver"
            else:
                rank = "bronze"

        new_data = data.copy()
        new_data["board_channel_id"] = channel_id
        new_data["rank"] = rank
        if data.get("board_channel_id"):
            new_data["board_channel_id"] = data.get("board_channel_id")
        if data.get("rank"):
            new_data["rank"] = data.get("rank")

        # 원래 함수 호출
        return super().to_internal_value(new_data)


class PostNotGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    board = serializers.SlugRelatedField(
        slug_field="title", queryset=Board.objects.all()
    )

    class Meta:
        model = Post
        fields = [
            "user",
            "board",
            "title",
            "content",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        post = Post.objects.create(user=user, **validated_data)

        return post


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    board = serializers.SlugRelatedField(
        slug_field="board_channel_id", queryset=Board.objects.all()
    )
    bookmarked_by_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        exclude = [
            "bookmarked_by",
        ]

    def get_bookmarked_by_count(self, obj):
        return obj.bookmarked_by.count()


class CommentNotGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["post", "user", "content"]

    def create(self, validated_data):
        user = self.context["request"].user
        new_post = Comment.objects.create(user=user, **validated_data)
        return new_post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

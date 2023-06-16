from rest_framework import serializers
from .models import Board, Post, Comment
from users.serializers import UserSerializer


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = [
            "pk",
            "rank",
            "name",
            "context",
            "is_active",
        ]


class PostNotGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    board = serializers.SlugRelatedField(slug_field='name', queryset=Board.objects.all())
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
    board = serializers.SlugRelatedField(slug_field='name', queryset=Board.objects.all())
    
    class Meta:
        model = Post
        fields = "__all__"


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

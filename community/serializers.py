from rest_framework import serializers
from .models import Board, Post, Comment, PostImage
from users.serializers import UserSerializer

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'
        
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'

class PostNotGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = PostImageSerializer(many=True,required=False) 
    class Meta:
        model = Post
        fields = ['board','user','title','content','image']
    
    def create(self,validated_data):
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)
        
        return post 
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentNotGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['post','user','content']
        
    def create(self,validated_data):
        user = self.context['request'].user
        new_post = Comment.objects.create(user=user,**validated_data)
        return new_post 

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


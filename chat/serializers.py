from rest_framework import serializers
from .models import Chatroom, Message

from users.serializers import UserSerializer
from community.serializers import BoardSerializer
from community.models import Board

class ChatroomSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=True)
    board = BoardSerializer(read_only=True)
    
    class Meta:
        model = Chatroom
        fields = '__all__'
     
class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = '__all__'
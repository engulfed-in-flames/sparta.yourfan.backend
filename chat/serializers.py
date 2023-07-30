from rest_framework import serializers
from chat.models import Chatroom, Message

from users.serializers import UserSerializer
from community.serializers import BoardSerializer

class ChatroomSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=True)
    board = BoardSerializer(read_only=True)
    
    class Meta:
        model = Chatroom
        fields = ['user','board']
     
class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['chatroom','user','content','message_type','created_at']
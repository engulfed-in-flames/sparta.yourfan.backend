from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Chatroom,Message
from .serializers import ChatroomSerializer,MessageSerializer
# Create your views here.

class ChatroomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
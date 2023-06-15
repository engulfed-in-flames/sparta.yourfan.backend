from rest_framework import viewsets
from .models import Chatroom,Message
from .serializers import ChatroomSerializer,MessageSerializer
# Create your views here.

class ChatroomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer
    
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
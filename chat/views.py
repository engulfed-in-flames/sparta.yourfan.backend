from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chatroom, Message
from .serializers import ChatroomSerializer, MessageSerializer

# Create your views here.


class ChatroomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chatroom.objects.all().order_by("-created_at")
    serializer_class = ChatroomSerializer
    lookup_field = "board__custom_url"

    @action(detail=True, methods=["GET"])
    def check(self, request, board__custom_url=None):
        chatroom = self.get_object()
        user = request.user

        is_duplicate = chatroom.user.filter(pk=user.pk).exists()
        is_banned_user = chatroom.board.banned_users.filter(pk=user.pk).exists()

        if is_duplicate:
            return Response(
                {"message": "Duplicated user"}, status=status.HTTP_401_UNAUTHORIZED
            )
        elif is_banned_user:
            return Response(
                {"message": "Banned user"}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from chat.models import Chatroom, Message
from chat.serializers import ChatroomSerializer, MessageSerializer

'''
채팅방과 관련된 viewset입니다. check method를 통해 접속가능한지 여부를 체크할 수 있습니다.
ReadOnlyViewSet이기 때문에 check 메소드 외에 조회 요청만 존재합니다. 
'''

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
                {"message": "중복 접속된 유저입니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        elif is_banned_user:
            return Response(
                {"message": "차단된 유저입니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({"message": "채팅방 접속 가능."}, status=status.HTTP_200_OK)


'''메세지 출력을 위한 viewset입니다. 마찬가지로 ReadOnlyViewSet 이기에 조회만 가능합니다'''

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import json
import logging
import redis


r = redis.Redis(host=settings.REDIS_CHANNEL_HOST, port=6379, db=0)


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("chat.consumers")
        self.groups = []

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["board"][1:]
        self.room_group_name = f"chat_{self.room_name}"
        self.chat_room = await self.get_chatroom("@" + self.room_name)

        self.user = self.scope["user"]

        await self.accept()  # 먼저 연결 수락

        if await self.is_user_connected(self.chat_room, self.user):
            await self.send(
                text_data=json.dumps(
                    {"error": "duplicate_connection", "message": "이미 연결된 상태입니다"}
                )
            )
            await self.close()  # 연결 끊기
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.add_user_to_chatroom(self.chat_room, self.user)
        self.logger.info(
            f'User {self.scope["user"].id}({self.scope["user"].nickname}) connected to chatroom "{self.room_name}"'
        )

        count = await self.chatroom_count(self.chat_room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_count",
                "count": int(count),
            },
        )


    async def disconnect(self, close_code):
        count = await self.chatroom_count(self.chat_room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_count",
                "count": int(count),
            },
        )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.remove_user_from_chatroom(self.chat_room, self.user)
        self.logger.info(
            f'User {self.scope["user"].id}({self.scope["user"].nickname}) disconnected from chatroom "{self.room_name}"'
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]
        user_nickname = self.scope["user"].nickname

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "user_nickname": user_nickname,
            },
        )

    async def chat_message(self, event):
        message_content = event["message"]
        user_nickname = event["user_nickname"]
        message = await self.save_message(message_content)

        await self.send(
            text_data=json.dumps(
                {
                    "message": message_content,
                    "user": user_nickname,
                    "chatroom": self.room_name,
                    "timestamp": str(message.created_at),
                }
            )
        )

    async def user_count(self, event):
        count = event["count"]

        # Send user count to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_count",
                    "count": count,
                }
            )
        )

    @database_sync_to_async
    def is_user_connected(self, chatroom, user):
        return chatroom.user.all().filter(email=user.email).exists()
        
    @database_sync_to_async
    def chatroom_count(self, chatroom):
        return chatroom.user.all().count()
        
    @database_sync_to_async
    def save_message(self, message_content):
        from .models import Message

        message = Message(
            user=self.user, chatroom=self.chat_room, content=message_content
        )
        message.save()

        return message

    @database_sync_to_async
    def get_chatroom(self, room_name):
        from .models import Chatroom

        return Chatroom.objects.get(board__custom_url=room_name)

    @database_sync_to_async
    def add_user_to_chatroom(self, chatroom, user):
        chatroom.user.add(user)

    @database_sync_to_async
    def remove_user_from_chatroom(self, chatroom, user):
        chatroom.user.remove(user)

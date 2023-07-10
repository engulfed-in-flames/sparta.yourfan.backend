from django.shortcuts import get_object_or_404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import json
import logging
import redis
import datetime

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

        entrance_message = f"{self.user.nickname}님이 입장하였습니다."
        current_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": entrance_message,
                "user_nickname": "[system]",
                "message_type": "SYSTEM",
                "timestamp": current_time,
            },
        )

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

        recent_messages = await self.get_recent_messages(self.chat_room)
        if recent_messages:
            await self.send(text_data=json.dumps(recent_messages))

    async def disconnect(self, close_code):
        
        count = await self.chatroom_count(self.chat_room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_count",
                "count": int(count) - 1,
            },
        )
        await self.remove_user_from_chatroom(self.chat_room, self.user)
        self.logger.info(
            f'User {self.scope["user"].id}({self.scope["user"].nickname}) disconnected from chatroom "{self.room_name}"'
        )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]
        user_nickname = self.scope["user"].nickname
        message_type = "USER"
        message = await self.save_message(message_content, message_type)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "user_nickname": user_nickname,
                "message_type": message_type,
                "timestamp": str(message.created_at),
            },
        )

    async def chat_message(self, event):
        message_content = event["message"]
        user_nickname = event["user_nickname"]
        message_type = event["message_type"]
        timestamp = event["timestamp"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message_content,
                    "user": user_nickname,
                    "chatroom": self.room_name,
                    "timestamp": timestamp,
                    "message_type": message_type,
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
    def get_recent_messages(self, chatroom):
        from .models import Message

        recent_messages = Message.objects.filter(
            chatroom=chatroom, message_type="USER"
        ).order_by("-created_at")[:5]
        if recent_messages:
            json_messages = [
                {
                    "message": message.content,
                    "user": "???",
                    "chatroom": self.room_name,
                    "timestamp": str(message.created_at),
                }
                for message in recent_messages
            ]
            return json_messages
        else:
            return None

    @database_sync_to_async
    def is_user_connected(self, chatroom, user):
        return chatroom.user.filter(pk=user.pk).exists()

    @database_sync_to_async
    def is_banned_user(self, chatroom, user):
        return chatroom.board.banned_users.filter(pk=user.pk).exists()

    @database_sync_to_async
    def chatroom_count(self, chatroom):
        return chatroom.user.all().count()

    @database_sync_to_async
    def save_message(self, message_content, message_type):
        from .models import Message

        message = Message(
            user=self.user,
            chatroom=self.chat_room,
            content=message_content,
            message_type=message_type,
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

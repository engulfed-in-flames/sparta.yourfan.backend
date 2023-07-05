from django.db import models
from django.conf import settings
from common.models import CommonModel


class Chatroom(CommonModel):
    board = models.ForeignKey("community.Board", on_delete=models.CASCADE)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Message(CommonModel):
    chatroom = models.ForeignKey("chat.Chatroom", on_delete=models.CASCADE)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=[('USER', 'User'), ('SYSTEM', 'System')], default='USER')

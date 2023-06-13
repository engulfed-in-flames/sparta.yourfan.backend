from django.db import models
from django.conf import settings

class Chatroom(models.Model):
    board = models.ForeignKey('community.Board', on_delete=models.CASCADE)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)

class Message(models.Model):
    chatroom = models.ForeignKey('chat.Chatroom', on_delete=models.CASCADE)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

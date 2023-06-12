from django.db import models
from community.models import Board
from django.contrib.auth import get_user_model
User = get_user_model()

class Chatroom(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ManyToManyField(User)

class Message(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

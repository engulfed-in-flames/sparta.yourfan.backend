from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Chatroom
from community.models import Board

@receiver(post_save, sender=Board)
def create_chatroom(sender, instance, created, **kwargs):
    if created: 
        Chatroom.objects.create(board=instance)
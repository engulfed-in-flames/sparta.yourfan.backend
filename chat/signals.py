from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Chatroom
from community.models import Board

'''
board 모델이 생성된 이후 실행되는 signal 입니다.
해당 board에 해당하는 채팅방 모델 Chatroom을 생성합니다.
'''

@receiver(post_save, sender=Board)
def create_chatroom(sender, instance, created, **kwargs):
    if created: 
        Chatroom.objects.create(board=instance)
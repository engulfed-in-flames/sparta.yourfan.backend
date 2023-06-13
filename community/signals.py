from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment

@receiver(post_save, sender=Comment)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.post.user.id}",
            {
                "type": "notify",  # Calls NotificationConsumer.notify
                "event": "New Comment",
                "nickname": instance.user.nickname,
                "comment": instance.content,
                "post": instance.post.title,
            },
        )
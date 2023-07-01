from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from common.models import CommonModel
from .youtube_api import topic_dict


class Topic(models.Model):
    topic_id = models.CharField(max_length=255)


# 해당 앱의 마이그레이션 이후에 한번만 실행하도록 설정
@receiver(post_migrate)
def create_topics(sender, **kwargs):
    if sender.name == "youtube" and not Topic.objects.exists():
        for topic_id, topic_name in topic_dict.items():
            Topic.objects.create(topic_id=topic_name)


class Channel(CommonModel):
    channel_id = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    custom_url = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    thumbnail = models.URLField()
    topic_id = models.ManyToManyField(Topic, blank=True)
    keyword = models.TextField(blank=True, null=True)
    banner = models.URLField(blank=True, null=True)
    upload_list = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChannelDetail(CommonModel):
    channel = models.ForeignKey(
        Channel, related_name="channel_detail", on_delete=models.CASCADE
    )
    total_view = models.IntegerField()
    subscriber = models.IntegerField()
    video_count = models.IntegerField()
    latest30_views = models.IntegerField(blank=True, null=True)
    latest30_likes = models.IntegerField(blank=True, null=True)
    latest30_comments = models.IntegerField(blank=True, null=True)
    rank = models.CharField(max_length=255, blank=True, null=True)
    participation_rate = models.CharField(max_length=255, blank=True, null=True)
    activity_rate = models.CharField(max_length=255, blank=True, null=True)
    avg_views = models.CharField(max_length=255, blank=True, null=True)
    avg_likes = models.CharField(max_length=255, blank=True, null=True)
    avg_comments = models.CharField(max_length=255, blank=True, null=True)
    like_per_view = models.CharField(max_length=255, blank=True, null=True)
    comment_per_view = models.CharField(max_length=255, blank=True, null=True)
    channel_activity = models.URLField(blank=True)
    channel_wordcloud = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.subscriber >= 10000000:
            self.rank = "diamond"
        elif self.subscriber >= 1000000:
            self.rank = "gold"
        elif self.subscriber >= 100000:
            self.rank = "silver"
        else:
            self.rank = "bronze"
        super().save(*args, **kwargs)

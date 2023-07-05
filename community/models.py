from django.db import models
from django.conf import settings
from django_bleach.models import BleachField

from youtube.models import Channel
from common.models import CommonModel


class Board(CommonModel):
    class RankKindChoices(models.TextChoices):
        DIAMOND = (
            "diamond",
            "다이아몬드",
        )
        GOLD = (
            "gold",
            "골드",
        )
        SILVER = (
            "silver",
            "실버",
        )
        BRONZE = (
            "bronze",
            "브론즈",
        )

    channel = models.ForeignKey(
        Channel, related_name="channel_board", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    custom_url = models.CharField(max_length=255, blank=True, null=True)
    board_channel_id = models.CharField(max_length=255, blank=True, null=True)

    rank = models.CharField(
        max_length=255,
        choices=RankKindChoices.choices,
        default="bronze",
    )
    is_active = models.BooleanField(default=True)

    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="subscribed_boards", blank=True
    )
    staffs = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="managed_boards", blank=True
    )
    banned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="banned_boards", blank=True
    )

    def save(self, *args, **kwargs):
        if self.channel:
            self.title = self.channel.title
            self.custom_url = self.channel.custom_url
        super().save(*args, **kwargs)


class Post(CommonModel):
    board = models.ForeignKey("community.Board", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=255)
    content = BleachField()
    bookmarked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="bookmarked_posts", blank=True
    )


class Comment(CommonModel):
    post = models.ForeignKey("community.Post", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = BleachField()


class StaffConfirm(CommonModel):
    class StaffStatus(models.TextChoices):
        PENDING = ("P", "Pending")
        APPROVED = ("A", "Approved")
        REJECTED = ("R", "Rejected")

    board = models.ForeignKey("community.Board", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2,
        choices=StaffStatus.choices,
        default=StaffStatus.PENDING,
    )

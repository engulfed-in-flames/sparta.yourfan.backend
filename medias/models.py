from django.db import models
from common.models import CommonModel


class Repost(CommonModel):
    imageURL = models.URLField(blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

from django.db import models
from django.conf import settings
from common.models import CommonModel


class Report(CommonModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )
    image_url = models.URLField(blank=True)
    cloudflare_image_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField()

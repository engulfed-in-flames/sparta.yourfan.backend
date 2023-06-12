from django.db import models
from common.models import CommonModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Shorts(CommonModel):
    title = models.CharField(max_length=200)
    context = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to='shorts/')
    
    uploader = models.ForeignKey(User,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, through="ShortsTag")

    def __str__(self):
        return self.title

class ShortsTag(models.Model):
    shorts = models.ForeignKey(Shorts, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
class Playlist(CommonModel):
    name = models.CharField(max_length=200)
    shorts = models.ManyToManyField(Shorts, related_name='playlists')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
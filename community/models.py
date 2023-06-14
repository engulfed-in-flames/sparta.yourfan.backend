from django.db import models
from django.conf import settings

class Board(models.Model):
    name = models.CharField(max_length=30)
    context = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='board_thumbnail/', blank=True, null=True)
    is_active = models.BooleanField(default=True)


class Post(models.Model):
    board = models.ForeignKey('community.Board', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey('community.Post', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PostImage(models.Model):
    post = models.ForeignKey('community.Post', on_delete=models.CASCADE)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

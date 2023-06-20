from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from time import time


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    username = models.CharField(max_length=20)
    email = models.EmailField(
        max_length=240,
        unique=True,
    )
    nickname = models.CharField("닉네임", max_length=16, null=True)
    avatar = models.URLField()    
    like = models.ManyToManyField("self", symmetrical=False, related_name="likes", blank=True, verbose_name="좋아요")
    # intro = models.TextField(blank=True, max_length=200)
    
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_consultant = models.BooleanField(default=False)
    is_writer = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "회원들"
        
    def activate(self):
        self.is_active = True
        self.save()
        return self
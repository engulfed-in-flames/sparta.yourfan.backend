from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


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
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(
        max_length=240,
        unique=True,
    )
    nickname = models.CharField("닉네임", max_length=20, unique=True)
    avatar = models.URLField()    
    like = models.ManyToManyField("self", symmetrical=False, related_name="likes", blank=True, verbose_name="좋아요")
        
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    is_consultant = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name_plural = "회원들"

import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.utils.base_models import CreateUpdateBaseModel

User = get_user_model()


class Profile(CreateUpdateBaseModel, models.Model):
    username = models.CharField(max_length=250, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='user_profile')
    image = models.ImageField(upload_to="users/profile/", null=True, blank=True)
    site = models.URLField(null=True, blank=True, max_length=250)
    interests = models.CharField(max_length=255, null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-id']

    def __str__(self):
        return self.username or self.full_name

    def save(self, *args, **kwargs):
        if not self.slug and self.username:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)


class PrivateChat(CreateUpdateBaseModel, models.Model):
    chat_id = models.UUIDField(default=uuid.uuid4(), unique=True, editable=False)
    user = models.ManyToManyField(User, related_name='private_chats', blank=True)

    class Meta:
        db_table = 'private_Chat'
        verbose_name = "Private Chat"
        verbose_name_plural = "Private Chats"


    def clean(self):
        if self.user.count() > 2:
            raise ValidationError("Ikki kishidan ortiq foydalanuvchi uchun ruhsat yoq")


class PrivateChatMessage(CreateUpdateBaseModel, models.Model):
    chat = models.ForeignKey(PrivateChat, related_name='private_chat_messages',
                             on_delete=models.CASCADE, )
    sender = models.ForeignKey(User, related_name='private_chat_sender',
                               on_delete=models.CASCADE)
    text = models.TextField()
    send_image = models.FileField(upload_to='chat/private/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'private_chat_messages'
        verbose_name = 'Private Chat message'
        verbose_name_plural = 'Private Chat messages'


class Story(CreateUpdateBaseModel, models.Model):
    profile = models.ForeignKey(Profile, related_name='profile_stories', on_delete=models.SET_NULL, null=True)
    content = models.FileField(upload_to='profile/story/', null=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    viewers = models.ManyToManyField(Profile, related_name='viewed_stories', blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.created_at + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_deleted(self):
        return timezone.now() > self.expires_at


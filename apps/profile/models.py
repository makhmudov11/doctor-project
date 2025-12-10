from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.utils import CustomResponse
from apps.utils.base_models import CreateUpdateBaseModel

User = get_user_model()


class Profile(CreateUpdateBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=250, null=True, unique=True, db_index=True)
    full_name = models.CharField(max_length=250, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="users/profile/image/", null=True, blank=True)
    website = models.URLField(null=True, blank=True, max_length=250)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return self.username or self.user.full_name

    def clean(self):
        super().clean()
        if self.username.rstrip():
            if " " in self.username:
                raise ValidationError(detail="Bo'sh joy bo'lishi mumkin emas.")



    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)

        if not self.full_name and self.user.full_name:
            self.full_name = self.user.full_name
        super().save(*args, **kwargs)


class StoryChoices(models.TextChoices):
    IMAGE = ('IMAGE', 'Image')
    VIDEO = ('VIDEO', 'Video')


class Story(CreateUpdateBaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='story')
    content = models.FileField(upload_to='users/profile/story/', null=True)
    content_type = models.CharField(max_length=100, null=True, choices=StoryChoices.choices)
    view_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)    # for delete

    def __str__(self):
        return self.profile.full_name or ''

    @property
    def media_type(self):
        if self.content:
            ext = self.content.name.split('.')[-1].lower()
            if ext in ['mp4', 'mov', 'avi']:
                return StoryChoices.VIDEO
            elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                return StoryChoices.IMAGE
        return 'unknown'

    def save(self, *args, **kwargs):
        Story.objects.filter(
            expires_at__lt=timezone.now(),
            expired=False
        ).update(expired=True)

        if self.content:
            ext = self.content.name.split('.')[-1].lower()
            if ext in ['mp4', 'mov', 'avi']:
                self.content_type = StoryChoices.VIDEO
            elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                self.content_type = StoryChoices.IMAGE
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


    def is_expired(self):
        return timezone.now() > self.expires_at

    def mark_viewed(self, viewer_profile):
        view, created = StoryView.objects.get_or_create(story=self, view_profile=viewer_profile)
        if created:
            self.view_count = StoryView.objects.filter(story=self).count()
            self.save(update_fields=['view_count'])



    class Meta:
        db_table = 'story'
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'
        ordering = ['-created_at']


class StoryView(CreateUpdateBaseModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_view')
    view_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='viewed_stories')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.view_profile.full_name} kordi {self.story.profile.full_name} ni storysini"

    class Meta:
        unique_together = ('story', 'view_profile')
        ordering = ['-viewed_at']

        db_table = 'story_view'
        verbose_name = 'Story View'
        verbose_name_plural = 'Story Viewers'

class FollowChoices(models.TextChoices):
    follow = ('follow', 'Follow')
    unfollow = ('unfollow', 'Unfollow')



class Follow(CreateUpdateBaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followers')
    status = models.CharField(max_length=50, null=True,
                              default=FollowChoices.follow,
                              choices=FollowChoices.choices)

    class Meta:
        unique_together = ('profile', 'following')

        db_table = 'follow'
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self):
        return f"{self.profile.full_name} --> {self.following.full_name}"

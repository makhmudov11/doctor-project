import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.users.choices import CustomUserRoleChoices
from apps.utils.base_models import CreateUpdateBaseModel
from apps.utils.generate_code import generate_public_id

User = get_user_model()


class PatientProfile(CreateUpdateBaseModel):
    public_id = models.PositiveIntegerField(unique=True, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=250, null=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="users/profile/image/", null=True, blank=True)
    website = models.URLField(null=True, blank=True, max_length=250)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'patient_profile'
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patients Profile'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name or  self.user.full_name or self.public_id


    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = getattr(self.user, "full_name", None)

        if not self.public_id:
            self.public_id = generate_public_id(PatientProfile)

        if not self.slug and self.full_name:
            self.slug = slugify(self.full_name.strip())

        super().save(*args, **kwargs)


class StoryChoices(models.TextChoices):
    IMAGE = ('IMAGE', 'Image')
    VIDEO = ('VIDEO', 'Video')


class Story(CreateUpdateBaseModel):
    public_id = models.PositiveIntegerField(unique=True, db_index=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story')
    role = models.CharField(
                            max_length=50,
                            choices=CustomUserRoleChoices.choices
                            )
    content = models.FileField(upload_to='users/profile/story/', null=True)
    content_type = models.CharField(max_length=100, null=True, choices=StoryChoices.choices)
    view_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)  # for delete

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

from django.contrib import admin
from apps.profile.models import Profile, Story, StoryView


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
    'public_id', 'username', 'full_name', 'user', 'followers_count', 'slug', 'following_count', 'posts_count',
    'is_private')
    search_fields = ('username', 'full_name', 'user__email')
    list_filter = ('is_private',)
    list_per_page = 20
    ordering = ('-created_at',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'public_id', 'profile', 'content_type', 'view_count', 'expires_at', 'is_expired_display']
    search_fields = ['profile__username', 'profile__full_name']
    list_filter = ['content_type']
    list_per_page = 20
    ordering = ['-created_at']
    readonly_fields = ['view_count']

    def is_expired_display(self, obj):
        return obj.is_expired()

    is_expired_display.boolean = True
    is_expired_display.short_description = 'EXPIRED'


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ('story', 'view_profile', 'viewed_at')
    search_fields = ('story__profile__username', 'view_profile__username')
    list_filter = ('story__content_type', 'viewed_at')
    list_per_page = 20
    ordering = ('-viewed_at',)

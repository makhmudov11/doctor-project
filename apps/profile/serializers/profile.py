from rest_framework import serializers

from apps.profile.models import Profile
from apps.users.serializers import UserSerializer


class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'full_name', 'bio', 'image', 'website']


class UserProfileListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'username', 'full_name', 'bio', 'image', 'website',
            'followers_count', 'following_count', 'posts_count', 'is_private',
            'slug', 'created_at', 'updated_at', 'deleted_at'
        ]


class UserProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'username', 'full_name', 'bio', 'image', 'website', 'is_private']

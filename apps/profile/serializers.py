from rest_framework import serializers
from apps.profile.models import Profile, Story, StoryChoices
from apps.users.serializers import UserSerializer
from apps.utils.CustomValidationError import CustomValidationError


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


class UserStoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['content']

    def validate(self, attrs):
        content_file = attrs.get('content')

        if not content_file:
            raise CustomValidationError(detail="Rasm yoki video fayl jo‘natilishi kerak")

        content_type = content_file.content_type
        if content_type.startswith('image'):
            attrs['content_type'] = StoryChoices.IMAGE
        elif content_type.startswith('video'):
            attrs['content_type'] = StoryChoices.VIDEO
        else:
            raise CustomValidationError(detail="Faqat rasm yoki video yuklash mumkin.")

        return attrs


class UserStoryListSerializer(serializers.ModelSerializer):
    profile = UserProfileListSerializer(read_only=True)

    class Meta:
        model = Story
        fields = [
            'id', 'profile', 'content', 'content_type',
            'view_count', 'expires_at',
            'created_at', 'updated_at', 'deleted_at'
        ]


class StoryElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'content', 'content_type', 'view_count', 'expires_at', 'created_at', 'updated_at', 'deleted_at']


class UserActiveStoriesSerializer(serializers.Serializer):
    profile = UserProfileListSerializer(read_only=True)
    stories = StoryElementSerializer(many=True, read_only=True)


class UserStoryMarkViewedSerializer(serializers.Serializer):
    profile = UserProfileListSerializer()
    story = StoryElementSerializer()


class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'full_name', 'bio', 'image', 'website']

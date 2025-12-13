from rest_framework import serializers

from apps.profile.models import Story, StoryChoices
from apps.profile.serializers.profile import UserProfileListSerializer
from apps.utils.CustomValidationError import CustomValidationError




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

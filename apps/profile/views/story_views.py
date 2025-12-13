from django.db import IntegrityError, transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from apps.admin.permissions.users import AdminPermission
from apps.profile.filters import UserStoryListFilter
from apps.profile.models import StoryView, Story, Profile
from apps.profile.paginations import UserStoryListPagination
from apps.profile.permission import UserActiveStoryPermission
from apps.profile.serializers.story import UserStoryMarkViewedSerializer, UserActiveStoriesSerializer, \
    StoryElementSerializer, \
    UserStoryListSerializer, UserStoryCreateSerializer
from apps.utils import CustomResponse


class UserStoryCreateAPIView(CreateAPIView):
    serializer_class = UserStoryCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        user_profile = Profile.objects.filter(user=self.request.user).first()
        if not user_profile:
            return CustomResponse.error_response(message='Userga tegishli profil mavjud emas')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        story = serializer.save(profile=self.request.user.profile)
        full_data = UserStoryListSerializer(story).data
        return CustomResponse.success_response(message='Storis muvaffaqiyatli yaratildi', data=full_data,
                                               code=HTTP_201_CREATED)


class UserStoryListAPIView(ListAPIView):
    serializer_class = UserStoryListSerializer
    permission_classes = [AdminPermission]
    pagination_class = UserStoryListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status']
    filterset_class = UserStoryListFilter
    search_fields = ['profile__username', 'profile__full_name']
    ordering_fields = ['created_at', 'updated_at', 'expires_at', 'profile__full_name']
    ordering = ['id']

    def get_queryset(self):
        return Story.objects.select_related('profile', 'profile__user')


class UserActiveStoryListAPIView(ListAPIView):
    serializer_class = StoryElementSerializer
    permission_classes = [UserActiveStoryPermission]

    def get_queryset(self):
        return Story.objects.filter(
            expires_at__gte=timezone.now(),
            profile__user=self.request.user,
            expired=False
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        profile = self.request.user.profile
        stories = self.get_queryset()
        serializer = UserActiveStoriesSerializer({
            "profile": profile,
            "stories": stories
        })
        return Response(serializer.data)


class UserStoryMarkViewedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, story_id):
        view_profile = self.request.user.profile
        if not view_profile:
            return CustomResponse.error_response(message='Userga tegishli profil topilmadi')

        try:
            story = Story.objects.get(
                id=story_id
            )
        except Story.DoesNotExist:
            return CustomResponse.error_response(message='Storis topilmadi')
        if story.profile == self.request.user.profile:
            return CustomResponse.error_response(message="O'z storisini koryapti")
        try:
            with transaction.atomic():
                view, created = StoryView.objects.get_or_create(
                    story=story,
                    view_profile=view_profile
                )

                if created:
                    story.view_count = story.story_view.count()
                    story.save(update_fields=['view_count'])

        except IntegrityError:
            return CustomResponse.error_response(message='Storyni belgilashda xatolik yuz berdi')
        serializer = UserStoryMarkViewedSerializer(
            instance={
                "profile": view.story.profile,
                "story": story
            })
        return CustomResponse.success_response(serializer.data)

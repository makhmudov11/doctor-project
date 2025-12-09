from django.db.models import F
from django.db import transaction, IntegrityError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from apps.admin.permissions.users import AdminPermission
from apps.profile.filters import UserProfileListFilter, UserStoryListFilter
from apps.profile.models import Profile, Story, StoryView, Follow, FollowChoices
from apps.profile.paginations import UserProfileListPagination, UserStoryListPagination
from apps.profile.permission import UserActiveStoryPermission
from apps.profile.serializers import UserProfileListSerializer, UserProfileDetailSerializer, UserStoryCreateSerializer, \
    UserStoryListSerializer, StoryElementSerializer, UserActiveStoriesSerializer, UserStoryMarkViewedSerializer
from apps.users.permissions import UserListPermission
from apps.utils import CustomResponse


class UserProfileListAPIView(ListAPIView):
    serializer_class = UserProfileListSerializer
    permission_classes = [UserListPermission]
    queryset = Profile.objects.select_related('user')
    pagination_class = UserProfileListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_private']
    filterset_class = UserProfileListFilter
    search_fields = ['username', 'full_name']
    ordering_fields = ['created_at', 'updated_at', 'full_name']
    ordering = ['id']


class UserProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileListSerializer
        return UserProfileDetailSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        full_fields_response = UserProfileListSerializer(instance)
        return Response(full_fields_response.data)

    # def get_object(self):
    #     return self.request.user


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


class UserProfileFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id):
        profile = request.user.profile

        try:
            following_user = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return CustomResponse.error_response(
                message=f'{profile_id}-idlik profil mavjud emas'
            )

        follow_obj, created = Follow.objects.get_or_create(
            profile=profile,
            following=following_user,
            defaults={"status": FollowChoices.follow}
        )

        if not created and follow_obj.status == FollowChoices.follow:
            return CustomResponse.error_response(message="Siz allaqachon follow qilgansiz")

        follow_obj.status = FollowChoices.follow
        follow_obj.save(update_fields=['status'])

        data = {
            "user": UserProfileDetailSerializer(profile).data,
            "following_user": UserProfileDetailSerializer(following_user).data,
        }
        return CustomResponse.success_response(data=data)


class UserUnFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id):
        if not profile_id:
            return CustomResponse.error_response(message='Profile id kelishi shart')

        profile = request.user.profile
        if not profile:
            return CustomResponse.error_response(message='Userga tegishli profil topilmadi')

        try:
            unfollowing_user = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return CustomResponse.error_response(
                message=f'{profile_id}-idlik userga tegishli profil mavjud emas'
            )

        is_following = Follow.objects.select_related('profile', 'following').filter(
            profile=profile,
            following=unfollowing_user,
            status=FollowChoices.follow
        ).first()

        if not is_following:
            return CustomResponse.error_response(
                message=f'Siz {unfollowing_user.full_name or unfollowing_user.username} ga follow bolmagansiz'
            )

        is_following.status = FollowChoices.unfollow
        is_following.save(update_fields=['status'])
        user = UserProfileListSerializer(profile).data
        unfollowing_user = UserProfileListSerializer(unfollowing_user).data

        return CustomResponse.success_response(
            message='Unfollow muvaffaqiyatli bajarildi.',
            data={
                "user": user,
                "unfollowing_user": unfollowing_user
            }
        )

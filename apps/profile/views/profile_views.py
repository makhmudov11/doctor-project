from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from apps.profile.filters import UserProfileListFilter
from apps.profile.models import Profile
from apps.profile.paginations import UserProfileListPagination
from apps.profile.permission import UserProfileDetailPermission
from apps.profile.serializers.profile import UserProfileCreateSerializer, UserProfileListSerializer, \
    UserProfileDetailSerializer
from apps.users.choices import CustomUserRoleChoices
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


class UserProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileListSerializer
    lookup_field = 'public_id'
    lookup_url_kwarg = 'profile_public_id'

    def get_queryset(self):
        return Profile.objects.select_related("user")


class UserProfileCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileCreateSerializer
    queryset = Profile.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save(user=request.user)

        data = UserProfileListSerializer(profile).data
        return CustomResponse.success_response(data=data, code=HTTP_201_CREATED)



class UserMyProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = [UserProfileDetailPermission]
    serializer_class = UserProfileListSerializer

    def get_object(self):
        return Profile.objects.select_related("user").get(user=self.request.user)


class UserMyProfileDetailRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [UserProfileDetailPermission]
    serializer_class = UserProfileListSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        return Profile.objects.select_related("user").get(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return self.serializer_class
        return UserProfileDetailSerializer

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()

        profile.delete()

        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])

        return CustomResponse.success_response(
            message="Profil o‘chirildi va akkaunt deaktiv qilindi",
            code=HTTP_204_NO_CONTENT
        )

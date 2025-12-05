from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.admin.filters.profile import AdminUserProfileListFilter
from apps.admin.paginations.profile import AdminUserProfileListPagination
from apps.admin.permissions.users import AdminPermission
from apps.admin.serializers.profile import AdminUserProfileListSerializer, AdminProfileCreateSerializer, \
    AdminUserProfileRetrieveUpdateDestroy
from apps.profile.models import Profile


class AdminUserProfileListAPIView(ListAPIView):
    serializer_class = AdminUserProfileListSerializer
    permission_classes = [AdminPermission]
    queryset = Profile.objects.all()
    pagination_class = AdminUserProfileListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_private']
    filterset_class = AdminUserProfileListFilter
    search_fields = ['username', 'full_name']
    ordering_fields = ['created_at', 'updated_at', 'full_name']
    ordering = ['id']

class AdminUserProfileCreateAPIView(CreateAPIView):
    serializer_class = AdminProfileCreateSerializer
    permission_classes = [AdminPermission]
    queryset = Profile.objects.all()

class AdminUserProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserProfileRetrieveUpdateDestroy
    permission_classes = [AdminPermission]
    queryset = Profile.objects.all()
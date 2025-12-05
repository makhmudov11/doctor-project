from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters

from apps.admin.filters.users import UserListFilter
from apps.admin.paginations.users import AdminUserListPagination
from apps.admin.permissions.users import AdminPermission
from apps.admin.serializers.users import AdminUserListSerializer, AdminUserCreateSerializer, \
    AdminUserRetrieveUpdateDestroySerializer

User = get_user_model()

class AdminUserListAPIView(ListAPIView):
    permission_classes = [AdminPermission]
    serializer_class = AdminUserListSerializer
    pagination_class = AdminUserListPagination
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_staff']
    filterset_class = UserListFilter
    search_fields = ['full_name', 'contact', 'role', 'contact_type', 'gender']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['-created_at']



class AdminUserCreateAPIView(CreateAPIView):
    serializer_class = AdminUserCreateSerializer
    permission_classes = [AdminPermission]
    queryset = User.objects.all()


class AdminUserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserRetrieveUpdateDestroySerializer
    permission_classes = [AdminPermission]
    queryset = User.objects.all()



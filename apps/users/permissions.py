from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class UserListPermission(BasePermission):

    def has_permission(self, request, view):
        if not bool(request.user.is_authenticated and request.user.is_staff):
            raise PermissionDenied(detail="Foydalanuvchilarni ko'rish admin uchun rucsat etilgan")
        return True


class UserDetailPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return  request.user == obj

from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.is_staff:
            if request.method in ['GET', 'PATCH']:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.is_staff:
            if request.method in ['GET', 'PATCH']:
                return True

        return False

from rest_framework.permissions import BasePermission

from apps.users.choices import CustomUserRoleChoices


class UserActiveStoryPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.profile.user)


class UserProfileDetailPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.profile.user)


class PatientPermission(BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                request.user.active_role == CustomUserRoleChoices.FOYDALANUVCHI
        )

    def has_object_permission(self, request, view, obj):
        return (
                request.user.active_role == CustomUserRoleChoices.FOYDALANUVCHI and
                getattr(obj, "user", None) == request.user
        )

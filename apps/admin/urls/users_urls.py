from django.urls import path

from apps.admin.views.users import AdminUserListAPIView, AdminUserListCreateAPIView

urlpatterns = [
    path('list/', AdminUserListAPIView.as_view(), name='admin-user-list'),
    path('create/', AdminUserListCreateAPIView.as_view(), name='admin-user-create'),
]
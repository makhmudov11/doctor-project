from django.urls import path

from apps.admin.views.users import AdminUserListAPIView, AdminUserCreateAPIView, AdminUserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('list/', AdminUserListAPIView.as_view(), name='admin-user-list'),
    path('create/', AdminUserCreateAPIView.as_view(), name='admin-user-create'),
    path('detail/<int:pk>/', AdminUserRetrieveUpdateDestroyAPIView.as_view(), name='admin-user-detail'),
]
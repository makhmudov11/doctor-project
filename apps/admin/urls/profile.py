from django.urls import path

from apps.admin.views.profile import AdminUserProfileListAPIView, AdminUserProfileCreateAPIView, \
    AdminUserProfileRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('list/', AdminUserProfileListAPIView.as_view(), name='admin-profile-list'),
    path('create/', AdminUserProfileCreateAPIView.as_view(), name='admin-profile-create'),
    path('detail/<int:pk>', AdminUserProfileRetrieveUpdateDestroyAPIView.as_view(), name='admin-profile-detail'),
]
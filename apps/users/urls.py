from django.urls import path

from apps.users.views import (RegisterCreateAPIView, LoginAPIView, VerifyCodeAPIView, ResendCode,
                              UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView)
app_name = 'users'

urlpatterns = [
    path('register/', RegisterCreateAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify/', VerifyCodeAPIView.as_view(), name='verify'),
    path('resend/', ResendCode.as_view(), name='resend_code'),
    path('list/', UserListCreateAPIView.as_view(), name='user_list'),
    path('detail/<int:pk>', UserRetrieveUpdateDestroyAPIView.as_view(), name='user_list'),
]


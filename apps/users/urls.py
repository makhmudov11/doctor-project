from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from apps.users.views import (RegisterCreateAPIView, LoginAPIView, VerifyCodeAPIView, ResendCode,
                              UserRetrieveUpdateAPIView,
                              )
app_name = 'users'

urlpatterns = [
    path('register/', RegisterCreateAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify/', VerifyCodeAPIView.as_view(), name='verify'),
    path('resend/', ResendCode.as_view(), name='resend_code'),
    path('detail/', UserRetrieveUpdateAPIView.as_view(), name='user_detail'),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
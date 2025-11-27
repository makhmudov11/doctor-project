from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.users.views import (RegisterCreateAPIView, LoginAPIView, VerifyCodeAPIView, ResendCode, UserModelViewSet)
app_name = 'users'

urlpatterns = [
    path('register/', RegisterCreateAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify/', VerifyCodeAPIView.as_view(), name='verify'),
    path('resend/', ResendCode.as_view(), name='resend_code')
]

router = SimpleRouter()
router.register('', UserModelViewSet, 'users')
urlpatterns += router.urls
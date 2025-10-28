from django.urls import path

from apps.users.views import LoginAPIView, verify_code, RegisterCreateAPIView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterCreateAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify_code/', verify_code, name='verify_code')
]

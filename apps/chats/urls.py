from django.urls import path

from apps.users.views import LoginAPIView, verify_code, RegisterCreateAPIView

app_name = 'chats'

urlpatterns = []

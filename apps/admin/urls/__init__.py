from django.urls import path, include

app_name = 'admin'

urlpatterns = [
    path('users/', include('apps.admin.urls.users')),
    path('users/profile/', include('apps.admin.urls.profile'))
]
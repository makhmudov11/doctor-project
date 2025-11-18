from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.users.models import SmsCode

# Register your models here.

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'contact', 'contact_type', 'status', 'active_role', 'is_staff']

@admin.register(SmsCode)
class AdminSmsCode(admin.ModelAdmin):
    list_display = ['id', 'contact', 'expires_at', 'hash_code', 'verified']
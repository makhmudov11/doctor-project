from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.users.models import SmsCode

# Register your models here.

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'contact', 'contact_type', 'password', 'status', 'active_role', 'gender', 'created_at', 'is_staff']

@admin.register(SmsCode)
class SmsCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'contact', 'expires_at', 'hash_code', 'verified', '_type', 'resend_code', 'attempts', 'delete_obj']
from django.contrib import admin

from apps.chats.models import Profile


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'full_name', 'bio', 'site']
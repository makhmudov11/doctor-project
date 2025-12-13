from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed


def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    update_last_login(sender=None, user=user)
    refresh = RefreshToken.for_user(user)
    refresh['active_role'] = user.active_role

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

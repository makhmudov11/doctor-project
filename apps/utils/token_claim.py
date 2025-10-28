from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed


def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)
    if user.email:
        refresh['email'] = user.email
    else:
        refresh['phone_number'] = user.phone_number

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

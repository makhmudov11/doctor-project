import jwt
import requests as external_requests
from django.contrib.auth import get_user_model
from jwt import PyJWKClient
from rest_framework import status
from google.auth.transport import requests

from apps.users.models import UserSocialAuthRegistrationTypeChoices, UserContactTypeChoices
from apps.users.serializers import UserSerializer
from apps.users.social_auth.save_picture import save_profile_picture_from_url
from apps.utils import CustomResponse
from apps.utils.token_claim import get_tokens_for_user
from config.settings import SOCIAL_AUTH_KEYS
from google.oauth2 import id_token
from rest_framework.views import APIView

from apps.users.social_auth.serializers import UserGoogleSocialAuthSerializer, UserFacebookSocialAuthSerializer, \
    UserAppleSocialAuthSerializer

User = get_user_model()


class UserGoogleSocialAuthAPIView(APIView):
    serializer_class = UserGoogleSocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")

        try:
            id_info = id_token.verify_oauth2_token(
                token, requests.Request(), SOCIAL_AUTH_KEYS['GOOGLE']['GOOGLE_CLIENT_ID']
            )

            if id_info.get("aud") != SOCIAL_AUTH_KEYS['GOOGLE']['GOOGLE_CLIENT_ID']:
                return CustomResponse.error_response(message='Token tekshirishda xatolik',
                                                     code=status.HTTP_403_FORBIDDEN)

            email = id_info.get("email")
            given_name = id_info.get("given_name", "")
            family_name = id_info.get("family_name", "")
            picture_url = id_info.get("picture", "")

            user, created = User.objects.get_or_create(
                contact=email,
                defaults={
                    "contact_type": UserContactTypeChoices.EMAIL,
                    "status": True,
                    "full_name": f"{given_name} {family_name}".strip(),
                    "registration_type": UserSocialAuthRegistrationTypeChoices.GOOGLE
                }
            )

            if picture_url and created:
                save_profile_picture_from_url(user=user, picture_url=picture_url)

            if created:
                message = "Google orqali muvaffaqiyatli ro'yhatdan o'dingiz."
            else:
                message = "Google orqali login muvaffaqiyatli bajarildi."

            token = get_tokens_for_user(user)
            user = UserSerializer(user).data
            return CustomResponse.success_response(
                message=message,
                data={
                    "token": token,
                    "user": user
                }
            )
        except ValueError:
            return CustomResponse.error_response(
                message="Token yaroqsiz",
                code=status.HTTP_403_FORBIDDEN
            )


class UserFacebookSocialAuthAPIView(APIView):
    serializer_class = UserFacebookSocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data.get("access_token")

        try:
            # Validate the token
            url = (f"https://graph.facebook.com/debug_token?input_token={access_token}"
                   f"&access_token={SOCIAL_AUTH_KEYS['FACEBOOK']['FACEBOOK_CLIENT_ID']}|"
                   f"{SOCIAL_AUTH_KEYS['FACEBOOK']['FACEBOOK_SECRET']}")
            data = external_requests.get(url).json()

            if "error" in data.get("data", {}):
                return CustomResponse.error_response(
                    message="Facebook token yaroqsiz yoki muddati tugagan",
                    code=status.HTTP_400_BAD_REQUEST
                )

            # Get user info
            user_info_url = f"https://graph.facebook.com/me?fields=id,name,email,picture&access_token={access_token}"
            user_data = external_requests.get(user_info_url).json()

            email = user_data.get("email", "")
            name = user_data.get("name", "")
            profile_pic_url = user_data.get("picture", {}).get("data", {}).get("url", "")

            if not email:
                return CustomResponse.error_response(
                    message='Facebook foydalanuvchidan email olinmadi, loginni yakunlab bo‘lmadi',
                    code=status.HTTP_400_BAD_REQUEST
                )

            # Create or get user
            user, created = User.objects.get_or_create(
                contact=email,
                defaults={
                    "contact_type": UserContactTypeChoices.EMAIL,
                    "status": True,
                    "full_name": name.strip(),
                    "registration_type": UserSocialAuthRegistrationTypeChoices.FACEBOOK
                }
            )

            if profile_pic_url and created:
                save_profile_picture_from_url(user=user, picture_url=profile_pic_url)

            token = get_tokens_for_user(user)
            user = UserSerializer(user).data
            if created:
                message = "Facebook orqali muvaffaqiyatli ro'yhatdan o'dingiz."
            else:
                message = "Facebook orqali login muvaffaqiyatli bajarildi."
            return CustomResponse.success_response(
                message=message,
                data={
                    "token": token,
                    "user": user
                }
            )
        except ValueError:
            return CustomResponse.error_response(
                message="Facebook tokenini tekshirishda xatolik",
                code=status.HTTP_403_FORBIDDEN
            )


class UserAppleSocialAuthAPIView(APIView):
    serializer_class = UserAppleSocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        identity_token = serializer.validated_data.get("identity_token")

        try:
            jwks_client = PyJWKClient(SOCIAL_AUTH_KEYS['APPLE']['APPLE_PUBLIC_URL'])

            signing_key = jwks_client.get_signing_key_from_jwt(identity_token).key

            decoded = jwt.decode(
                identity_token,
                signing_key,
                algorithms=["RS256"],
                audience=SOCIAL_AUTH_KEYS['APPLE']['APPLE_CLIENT_ID'],  # IMPORTANT: must match Apple app Services ID
                issuer="https://appleid.apple.com",
            )

            apple_user_id = decoded.get("sub")
            email = decoded.get("email", '')
        except Exception as e:
            return CustomResponse.error_response(
                message=f"Apple token yaroqsiz: {e}",
                code=status.HTTP_400_BAD_REQUEST
            )

        if not email:
            return CustomResponse.error_response(
                message='Apple email olishda xatolik',
                code=status.HTTP_400_BAD_REQUEST
            )
        user, created = User.objects.get_or_create(
            contact=email,
            defaults={
                "status": True,
                "contact_type": UserContactTypeChoices.EMAIL,
                "full_name": serializer.validated_data.get("full_name", '').strip(),
                "registration_type": UserSocialAuthRegistrationTypeChoices.APPLE,
            }
        )

        if created:
            default_avatar_url = f"https://www.gravatar.com/avatar/{hash(email.lower())}?d=identicon"
            save_profile_picture_from_url(user=user, picture_url=default_avatar_url)

        token = get_tokens_for_user(user)
        user = UserSerializer(user).data
        if created:
            message = "Apple orqali muvaffaqiyatli ro'yhatdan o'dingiz."
        else:
            message = "Apple orqali login muvaffaqiyatli bajarildi."

        return CustomResponse.success_response(
            message=message,
            data={
                "token": token,
                "user": user
            }
        )

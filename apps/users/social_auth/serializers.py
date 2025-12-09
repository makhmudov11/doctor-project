from rest_framework import serializers
from rest_framework import status

from apps.utils.CustomValidationError import CustomValidationError


class UserGoogleSocialAuthSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)

    def validate(self, attrs):
        token = attrs.get('token', '')
        if not token:
            raise CustomValidationError(detail='Token kelishi shart', code=status.HTTP_403_FORBIDDEN)
        return attrs


class UserFacebookSocialAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=255)

    def validate(self, attrs):
        access_token = attrs.get('access_token', '')
        if not access_token:
            raise CustomValidationError(detail='Token kelishi shart', code=status.HTTP_403_FORBIDDEN)
        return attrs

class UserAppleSocialAuthSerializer(serializers.Serializer):
    identity_token = serializers.CharField(max_length=255)
    full_name = serializers.CharField(max_length=100, required=False)

    def validate(self, attrs):
        identity_token = attrs.get('identity_token', '')
        if not identity_token:
            raise CustomValidationError(detail='Token kelishi shart', code=status.HTTP_403_FORBIDDEN)
        return attrs


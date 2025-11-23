from apps.users.serializers import UserSerializer, UserListSerializer, UserDetailSerializer

from rest_framework import serializers


class SwaggerMessageSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class SwaggerTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class SwaggerLoginDataSerializer(serializers.Serializer):
    user = UserSerializer()
    token = SwaggerTokenSerializer()


class SwaggerLoginSerializer(SwaggerMessageSuccessSerializer):
    data = SwaggerLoginDataSerializer()


class SwaggerRegisterSerializer(SwaggerMessageSuccessSerializer):
    data = UserSerializer()


class SwaggerVerifyCodeSerializer(SwaggerMessageSuccessSerializer):
    data = UserSerializer()

class SwaggerResendCodeDataSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=255)

class SwaggerResendCodeSerializer(SwaggerMessageSuccessSerializer):
    data = SwaggerResendCodeDataSerializer()

# class SwaggerUserListSerializer(SwaggerRegisterSerializer):
#     data = UserListSerializer(many=True)

class SwaggerUserRetrieveUpdateDestroySerializer(SwaggerMessageSuccessSerializer):
    data = UserDetailSerializer()
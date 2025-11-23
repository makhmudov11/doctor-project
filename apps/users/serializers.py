from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import SmsCode
from apps.utils.CustomValidationError import CustomValidationError
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(
        input_formats=["%d/%m/%Y"],
        format="%d/%m/%Y",
        required=True
    )

    class Meta:
        model = User
        fields = ['id', 'full_name', 'contact', 'birth_date', 'password', 'status']
        extra_kwargs = {
            "password": {"write_only": True},
            "status": {"read_only": True}
        }

    def create(self, validated_data):
        contact = validated_data.get('contact', "")
        user = User.objects.create(
            full_name=validated_data.get('full_name'),
            contact=contact,
            birth_date=validated_data.get('birth_date'),
            contact_type=validate_email_or_phone_number(contact)
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=30)

    def validate(self, attrs):
        contact = attrs.get('contact')
        password = attrs.get('password')

        if contact is None:
            raise CustomValidationError(detail="Email yoki telefon raqam kiritilishi shart.")

        if password is None:
            raise CustomValidationError(detail="Parol kiritilishi shart.")

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'contact', 'created_at', 'is_active', 'status']


class SmsCodeSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='contact', read_only=True)

    class Meta:
        model = SmsCode
        fields = ['id', 'user', 'created_at', 'attempts', 'verified', 'expires_at']
        extra_kwargs = {
            'attempts': {'read_only': True},
            'verified': {'read_only': True},
            'expires_at': {'read_only': True},
        }


class VerifyCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=200, required=True)
    code = serializers.CharField(max_length=100, required=True)

    def validate(self, attrs):
        code = attrs.get('code')
        if len(code) == 6:
            return attrs
        raise CustomValidationError(detail="Parol xato")



class ResendCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=200, required=True)

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'contact', 'full_name', 'birth_date', 'image', 'created_at', 'active_role', 'status']

class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'contact', 'full_name', 'birth_date', 'image', 'created_at', 'active_role', 'status']
        # extra_kwargs = {
        #     "image" : {"read_only" : True},
        #     "created_at" : {"read_only" : True},
        #     "active_role" : {"read_only" : True},
        #     "status" : {"read_only" : True},
        # }
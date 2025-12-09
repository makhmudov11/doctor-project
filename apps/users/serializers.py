from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.users.models import SmsCode, UserContactTypeChoices
from apps.utils.CustomValidationError import CustomValidationError
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(
        input_formats=["%d.%m.%Y"],
        format=["%d.%m.%Y"]
    )

    class Meta:
        model = User
        fields = ['id', 'full_name', 'contact', 'birth_date', 'gender', 'password', 'status', 'created_at']
        extra_kwargs = {
            "password": {"write_only": True},
            "status": {"read_only": True},
            "created_at": {"read_only": True}
        }

    def validate(self, attrs):
        contact = attrs.get('contact').strip()
        result = validate_email_or_phone_number(contact)

        if not result in [UserContactTypeChoices.EMAIL, UserContactTypeChoices.PHONE]:
            raise CustomValidationError(detail='Email yoki telefon raqam formati xato.')

        attrs['contact_type'] = result
        return attrs

    def create(self, validated_data):
        contact = validated_data.get('contact')
        user = User.objects.create(
            full_name=validated_data.get('full_name', None),
            contact=contact,
            birth_date=validated_data.get('birth_date'),
            contact_type=validated_data.get('contact_type'),
            gender=validated_data.get('gender', None)
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        contact = attrs.get('contact')
        password = attrs.get('password')

        if contact is None:
            raise CustomValidationError(detail="Email yoki telefon raqam kiritilishi shart.")

        if password is None:
            raise CustomValidationError(detail="Parol kiritilishi shart.")

        return attrs


class UserSerializer(serializers.ModelSerializer):
    last_login = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'contact', 'contact_type',
                  'active_role', 'image', 'birth_date', 'gender',
                  'status', 'last_login', 'is_active', 'is_staff', 'is_superuser',
                  'created_at', 'updated_at', 'deleted_at']

    @extend_schema_field(serializers.CharField())
    def get_last_login(self, obj):
        if obj.last_login:
            return (timezone.localtime(obj.last_login).strftime('%Y-%m-%d %H:%M:%S'))
        return None


class SmsCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SmsCode
        fields = ['id', 'contact', 'attempts', 'resend_code', 'verified',
                  'expires_at', 'delete_obj', '_type', 'created_at']


class VerifyCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=100)

    def validate(self, attrs):
        code = attrs.get('code', '').strip()
        if len(code) != 6:
            raise CustomValidationError(detail="Parol uzunligi 6 ta bo'lishi kerak")
        return attrs


class ResendCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=200, required=True)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'contact', 'full_name', 'birth_date', 'image', 'created_at', 'active_role', 'status']


class UserDetailSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'contact', 'full_name', 'birth_date', 'image', 'created_at', 'active_role', 'status']
        extra_kwargs = {
            "id": {"read_only": True},
            "contact": {"read_only": True},
            #     "image" : {"read_only" : True},
            "created_at": {"read_only": True},
            "active_role": {"read_only": True},
            "status": {"read_only": True},
        }


class UserForgotPasswordSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)

    def validate_contact(self, contact):
        contact = contact.strip()
        contact_type = validate_email_or_phone_number(contact)

        if contact_type not in [UserContactTypeChoices.EMAIL, UserContactTypeChoices.PHONE]:
            raise CustomValidationError(detail='Email yoki telefon formati xato.')

        return contact


class UserResetPasswordSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

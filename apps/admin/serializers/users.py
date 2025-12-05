from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.utils.CustomValidationError import CustomValidationError
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {
            "user" : rep
        }




class AdminUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'contact', 'password', 'birth_date', 'gender', 'status',
            'created_at', 'updated_at', 'deleted_at', 'image'
        ]
        extra_kwargs = {
            "contact": {"required": True},
            "password": {"write_only": True, "required": True},
            "deleted_at": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "image": {"allow_null": True, "required": False},
            "status": {"required": False},
        }

    def create(self, validated_data):
        contact = validated_data.get('contact', '').strip()
        if not contact:
            raise serializers.ValidationError("Contact yo'q")

        validated_data['contact'] = contact
        validated_data['contact_type'] = validate_email_or_phone_number(contact)

        password = validated_data.pop('password').strip()
        if not password:
            raise serializers.ValidationError("Password yo'q")

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminUserRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=50, write_only=True, required=True)
    password2 = serializers.CharField(max_length=50, write_only=True, required=True)

    birth_date = serializers.DateField(
        input_formats=["%d/%m/%Y"],
        format="%d/%m/%Y"
    )

    contact = serializers.CharField(max_length=100, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone_number',
                  'password1', 'password2', 'birth_date', 'contact']
        read_only_fields = ['email', 'phone_number']


    def validate(self, attrs):
        contact = attrs.get('contact')
        result = validate_email_or_phone_number(value=contact)
        if result == 'email':
            attrs['email'] = contact
        else:
            attrs['phone_number'] = contact

        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if password2 != password1:
            raise ValidationError("Parol bir biriga mos emas")

        return attrs



    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=30, required=True)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone_number', 'created_at', 'is_active', 'is_staff']
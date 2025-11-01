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
        extra_kwargs = {
            'email': {'read_only': True},
            'phone_number': {'read_only': True},
        }


    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if password2 != password1:
            raise ValidationError("Parol bir biriga mos emas")
        password = attrs.pop("password1")
        attrs["password"] = password
        attrs.pop("password2")

        return attrs



    def create(self, validated_data):
        contact = validated_data.get('contact')
        result = validate_email_or_phone_number(contact)
        if result == 'email':
            validated_data['email'] = contact
        elif result == 'phone_number':
            validated_data['phone_number'] = contact


        validated_data.pop("contact")

        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=30, required=True)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone_number', 'created_at', 'is_active', 'is_staff']
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import LoginSerializer, UserSerializer, RegisterSerializer
from apps.utils.generate_code import send_verification
from apps.utils.token_claim import get_tokens_for_user
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()

class RegisterCreateAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data.get('contact')
        if User.objects.filter(Q(email=contact) | Q(phone_number=contact)).exists():
            raise ValidationError({"error":
                                       f"""Ushbu {contact} {validate_email_or_phone_number(contact)} avval mavjud"""
                                   })
        full_name = serializer.validated_data.get('full_name')
        password = serializer.validated_data.get('password')
        birth_date = serializer.validated_data.get('birth_date')
        result = validate_email_or_phone_number(value=contact)
        data = {
            "contact" : contact,
            "full_name" : full_name,
            "birth_date" : birth_date,
            "password" : password
        }
        if result == 'email':
            send_verification(contact=contact, data=data)
            return Response(data={"message": f"{contact} ga kod yuborildi ✅"}, status=status.HTTP_200_OK)
        # else:
        #     ...  # nomerga jonatiladi


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data('contact')
        password = serializer.validated_data('password')

        result = validate_email_or_phone_number(value=contact)

        if result == 'email':
            user = authenticate(request, contact=contact, password=password)
            if user is None:
                return Response(data={"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)
            send_verification(contact)
            return Response(data={"message": f"{contact} ga kod yuborildi ✅"}, status=status.HTTP_200_OK)
        else:
            ...  # nomerga jonatiladi


@api_view(["POST"])
def verify_code(request):
    contact = request.data.get("contact")
    code = request.data.get("code")

    if not contact or not code:
        return Response({"error": "Kod kiritilmadi"}, status=400)

    contact = contact.strip().lower()
    saved_code = cache.get(contact)

    if saved_code is None:
        return Response({"error": "Kod topilmadi yoki muddati tugagan"}, status=400)

    if str(saved_code) != str(code):
        return Response({"error": "Kod noto‘g‘ri"}, status=400)

    try:
        user = User.objects.get(
            Q(email=contact) | Q(phone_number=contact)
        )
    except User.DoesNotExist:
        return Response("User topilmadi", status=status.HTTP_404_NOT_FOUND)

    token = get_tokens_for_user(user=user)
    serializer = UserSerializer(user)

    cache.delete(contact)
    return Response(data={
        "user": serializer.data,
        "token": token},
        status=status.HTTP_200_OK)

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework import status
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED

from apps.utils import CustomResponse
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import SmsCode
from apps.users.serializers import RegisterSerializer, LoginSerializer, UserSerializer, VerifyCodeSerializer
from apps.users.tasks import send_verification_code

from apps.utils.generate_code import generate_code
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
        if User.objects.filter(contact=contact).exists():
            return CustomResponse.error_response(message=f"{contact} orqali ro'yhatdan o'tilgan.")
        user = serializer.save()
        user = UserSerializer(user).data
        result = validate_email_or_phone_number(value=contact)
        if result == 'email':
            code = generate_code()
            try:
                SmsCode.create_for_contact(contact, make_password(code))
            except Exception as e:
                return CustomResponse.error_response(
                    message=f"Server xatosi, {str(e)}",
                    code=HTTP_500_INTERNAL_SERVER_ERROR
                )
            send_verification_code(email=contact, code=code)
            return CustomResponse.success_response(data={"user": user}, message="Kod yuborildi.")
        else:
            pass


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data.get('contact')
        password = serializer.validated_data.get('password')

        try:
            user = User.objects.get(contact=contact)
        except User.DoesNotExist:
            return Response({"data": {"error": "User topilmadi"}}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({"error": "Parol noto'g'ri"}, status=status.HTTP_401_UNAUTHORIZED)

        user = UserSerializer(user).data
        token = get_tokens_for_user(user)
        return Response(data={"user": user, "token": token}, status=status.HTTP_200_OK)


class VerifyCodeAPIView(APIView):
    serializer_class = VerifyCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data.get('contact')
        code = serializer.validated_data.get('code')
        if not code or not contact:
            return CustomResponse.error_response(message="Malumot toliq emas")
        user_codes = SmsCode.objects.filter(contact=contact, verified=False).last()
        if not user_codes:
            return CustomResponse.error_response(message="Kod topilmadi")

        if user_codes.expires_at < timezone.now():
            user_codes.delete()
            return CustomResponse.error_response(message="Kod yaroqsiz")

        if check_password(code, user_codes.hash_code):
            user = User.objects.filter(contact=contact).first()
            user.status = True
            user = user.save()
            user = UserSerializer(user).data
            user_codes.verified = True
            user_codes.save()
            return CustomResponse.success_response(message="Foydalanuvchi yaratildi",
                                                   data=user,
                                                   code=HTTP_201_CREATED)

        return CustomResponse.error_response(message="Kod noto‘g‘ri kiritildi", code=HTTP_401_UNAUTHORIZED)


class ResendCode(APIView):
    def post(self, request):
        contact = request.data.get('contact')

        if not contact:
            return CustomResponse.error_response(message="Malumot bo'sh bo'lishi mumkin emas.")

        user_codes = SmsCode.objects.filter(contact=contact, verified=False).last()

        if not user_codes:
            return CustomResponse.error_response(message="Kod topilmadi")

        if user_codes.attempts >= 3:
            user_codes.delete()
            try:
                User.objects.get(contact=contact).delete()
            except User.DoesNotExist:
                pass
            return CustomResponse.error_response(message="Urinishlar soni tugadi.")

        code = generate_code()
        send_verification_code(contact, code)

        user_codes.attempts += 1
        user_codes.save()
        return CustomResponse.success_response(data={"contact" : contact}, message="Kod qaytadan yuborildi.")

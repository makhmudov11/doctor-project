from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, \
    HTTP_404_NOT_FOUND

from apps.users.permissions import UserListPermission, UserDetailPermission
from apps.utils import CustomResponse
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView

from apps.users.models import SmsCode
from apps.users.serializers import RegisterSerializer, LoginSerializer, UserSerializer, VerifyCodeSerializer, \
    UserListSerializer, UserDetailSerializer, ResendCodeSerializer
from apps.users.tasks import send_verification_code

from apps.utils.generate_code import generate_code
from apps.utils.swagger.users.serializer import SwaggerLoginSerializer, SwaggerRegisterSerializer, \
    SwaggerVerifyCodeSerializer, SwaggerResendCodeSerializer, SwaggerUserRetrieveUpdateDestroySerializer
from apps.utils.token_claim import get_tokens_for_user
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class RegisterCreateAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    @extend_schema(
        request=RegisterSerializer,
        responses={
            200: OpenApiResponse(response=SwaggerRegisterSerializer)
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return CustomResponse.error_response(data=e.detail)

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
            return CustomResponse.success_response(message='qalesan')


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    @extend_schema(
        responses=SwaggerLoginSerializer,
    )
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data.get('contact')
        password = serializer.validated_data.get('password')

        try:
            user = User.objects.get(contact=contact)
        except User.DoesNotExist:
            return CustomResponse.error_response(message="User topilmadi", code=HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return CustomResponse.error_response(message="Parol noto'g'ri", code=HTTP_401_UNAUTHORIZED)

        token = get_tokens_for_user(user)
        user = UserSerializer(user).data

        return CustomResponse.success_response(
            message="Login muvaqqiyatli yakunlandi",
            data={"user": user, "token": token}
        )


class VerifyCodeAPIView(APIView):
    serializer_class = VerifyCodeSerializer

    @extend_schema(
        responses={
            201: SwaggerVerifyCodeSerializer},
        description="User yaratilgan boladi, statusi TRUE boladi."
    )
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

    @extend_schema(
        request=ResendCodeSerializer,
        responses=SwaggerResendCodeSerializer
    )
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
        return CustomResponse.success_response(data={"contact": contact}, message="Kod qaytadan yuborildi.")


class UserListCreateAPIView(ListCreateAPIView):
    serializer_class = UserListSerializer
    permission_classes = [UserListPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return User.objects.filter(status=True)


class UserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [UserDetailPermission]

    @extend_schema(
        responses=OpenApiResponse(
            response=SwaggerUserRetrieveUpdateDestroySerializer,
    )
    )

    def get_queryset(self):
        return User.objects.all()

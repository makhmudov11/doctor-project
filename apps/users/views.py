from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password

from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, \
    HTTP_404_NOT_FOUND

from apps.users.permissions import UserDetailPermission
from apps.utils import CustomResponse
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView

from apps.users.models import SmsCode, UserContactTypeChoices, SmsCodeTypeChoices
from apps.users.serializers import (RegisterSerializer, LoginSerializer, UserSerializer, VerifyCodeSerializer,
                                    UserDetailSerializer, ResendCodeSerializer, SmsCodeSerializer,
                                    UserForgotPasswordSerializer, UserResetPasswordSerializer, )

from apps.users.tasks import send_verification_code

from apps.utils.generate_code import generate_code
from apps.utils.token_claim import get_tokens_for_user
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class RegisterCreateAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        contact = request.data.get('contact', '').strip()
        password = request.data.get('password', '').strip()

        if not contact:
            return CustomResponse.error_response(
                message='Email yoki telefon raqam kiritilishi shart'
            )

        if not password:
            return CustomResponse.error_response(message='Parol kiritilishi shart.')

        if User.objects.filter(contact=contact, status=True).exists():
            return CustomResponse.error_response(
                message=f"{contact} orqali avval ro'yhatdan o'tilgan"
            )

        User.objects.filter(contact=contact, status=False).delete()

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user = UserSerializer(user).data

        contact_type = serializer.validated_data.get('contact_type')

        if contact_type == 'email':
            code = generate_code()

            try:
                SmsCode.create_for_contact(
                    contact=contact,
                    hash_code=make_password(code),
                    _type=SmsCodeTypeChoices.REGISTER
                )
                send_verification_code(email=contact, code=code)
                return CustomResponse.success_response(data={"user": user}, message="Kod yuborildi.")
            except Exception as e:
                return CustomResponse.error_response(message='Kod yuborishda xatolik.', data={"user": user})
        else:
            return CustomResponse.success_response(message='qalesan')


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data.get('contact').strip()
        password = serializer.validated_data.get('password').strip()

        try:
            user = User.objects.get(contact=contact, status=True)
        except User.DoesNotExist:
            return CustomResponse.error_response(message="User topilmadi", code=HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return CustomResponse.error_response(message="Parol noto'g'ri", code=HTTP_401_UNAUTHORIZED)

        user = UserSerializer(user).data

        contact_type = validate_email_or_phone_number(contact)
        if contact_type == UserContactTypeChoices.EMAIL:
            code = generate_code()
            user_code_obj = SmsCode.create_for_contact(contact=contact, hash_code=make_password(code),
                                                       _type=SmsCodeTypeChoices.LOGIN)
            user_code_data = SmsCodeSerializer(user_code_obj).data
            send_verification_code(email=contact, code=code)
            return CustomResponse.success_response(
                message='Kod yuborildi.',
                data={"user": user, "user_code_data": user_code_data}
            )
        else:
            pass


class VerifyCodeAPIView(APIView):
    serializer_class = VerifyCodeSerializer
    MAX_ATTEMPTS = 3

    def post(self, request):
        contact = request.data.get('contact', '').strip()
        if not contact:
            return CustomResponse.error_response(message='Email yoki telefon raqam kelishi shart')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get('code')

        user = User.objects.filter(contact=contact).first()
        if not user:
            return CustomResponse.error_response(message='User topilmadi')

        user_code_obj = SmsCode.objects.filter(
            contact=contact,
            verified=False,
            expires_at__gte=timezone.now()
        ).order_by('-created_at').first()

        if not user_code_obj:
            return CustomResponse.error_response(message="Kod topilmadi")

        if not check_password(code, user_code_obj.hash_code):
            user_code_obj.attempts += 1
            user_code_obj.save()

            if user_code_obj.attempts > self.MAX_ATTEMPTS:
                return CustomResponse.error_response(message="Urinishlar soni tugadi.")

            return CustomResponse.error_response(
                message=f"Kod noto'g'ri kiritildi.",
                data={
                    "sms_code_obj" : SmsCodeSerializer(user_code_obj).data,
                    "qolgan_urinishlar_soni" : self.MAX_ATTEMPTS - user_code_obj.attempts
                },

            )

        if user_code_obj._type == SmsCodeTypeChoices.REGISTER:
            user.status = True
            user.save()
            user_data = UserSerializer(user).data
            user_code_obj.verified = True
            user_code_obj.save()
            return CustomResponse.success_response(
                message="Registratsiya muvaffqaiyatli bajarildi, foydalanuvchi yaratildi",
                data=user_data, code=HTTP_201_CREATED)
        elif user_code_obj._type == SmsCodeTypeChoices.CHANGE_PASSWORD:
            user_code_obj.verified = True
            user_code_obj.save()
            return CustomResponse.success_response(
                message="Parol o'zgartirish uchun kod tasdiqlandi",
                data={"user": user}
            )
        else:
            user_code_obj.verified = True
            user_code_obj.save()
            token = get_tokens_for_user(user)
            user = UserSerializer(user).data
            return CustomResponse.success_response(
                message="Login muvaqqiyatli yakunlandi",
                data={"user": user, "token": token}
            )


class ResendCode(APIView):
    serializer_class = ResendCodeSerializer

    MAX_RESEND_CODE = 3

    def post(self, request):
        contact = request.data.get('contact', '').strip()

        if not contact:
            return CustomResponse.error_response(message="Email yoki telefon raqam kelishi shart.")

        user_code_obj = SmsCode.objects.filter(
            contact=contact,
            verified=False,
            delete_obj__gte=timezone.now()
        ).order_by('-created_at').first()

        if not user_code_obj:
            return CustomResponse.error_response(message='Kod topilmadi.')

        if user_code_obj.resend_code >= self.MAX_RESEND_CODE:
            return CustomResponse.error_response(
                message="Urinishlar soni tugadi.",
                data=SmsCodeSerializer(user_code_obj).data
            )

        code = generate_code()
        user_code_obj.resend_code += 1
        user_code_obj.expires_at = timezone.now() + timedelta(seconds=180)
        user_code_obj.attempts = 0
        user_code_obj.hash_code = make_password(code)
        user_code_obj.save()
        send_verification_code(contact, code)
        sms_code_obj = SmsCodeSerializer(user_code_obj).data
        return CustomResponse.success_response(
            data={
                "contact": contact,
                "sms_code_obj" : sms_code_obj,
                "qayta_jonatish_qoldi" : self.MAX_RESEND_CODE - sms_code_obj['resend_code']
            },
            message="Kod qaytadan yuborildi."
        )


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [UserDetailPermission]
    parser_classes = [MultiPartParser, FormParser]

    # def get_queryset(self):
    #     return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user


class UserForgotPasswordAPIView(APIView):
    serializer_class = UserForgotPasswordSerializer

    def post(self, request):
        contact = request.data.get('contact', '').strip()

        if not contact:
            return CustomResponse.error_response(message='Email yoki telefon raqam kelishi shart')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(contact=contact).first()

        if not user:
            return CustomResponse.error_response(message='User topilmadi')

        user = UserSerializer(user).data
        code = generate_code()
        SmsCode.create_for_contact(contact=contact, hash_code=make_password(code), _type='change-password')
        send_verification_code(email=contact, code=code)

        return CustomResponse.success_response(message='Parol tiklash uchun sms kod yuborildi.', data={"user": user})


class UserResetPasswordAPIView(APIView):
    serializer_class = UserResetPasswordSerializer
    permission_classes = []

    def post(self, request):
        contact = request.data.get('contact', '').strip()
        password = request.data.get('password', '').strip()

        if not contact:
            return CustomResponse.error_response(message='Email yoki telefon raqam kelishi shart')

        if not password:
            return CustomResponse.error_response(message='Parol kiritilishi shart')

        user_code_obj = SmsCode.objects.filter(contact=contact).order_by('-created_at').first()

        if user_code_obj.is_expired() or user_code_obj.verified:
            return CustomResponse.error_response(message="Kod almashtirish imkkoni yo'q")

        if not user_code_obj.verified:
            return CustomResponse.error_response(message="Sizda parol almashtirish uchun ruxsat yo'q")

        user = User.objects.filter(contact=contact).first()

        if not user:
            return CustomResponse.error_response(message='User topilmadi')

        user.set_password(password)
        user.save()
        user = UserSerializer(user).data
        return CustomResponse.success_response(message="Parol muvaffaqiyatli o'zgartirildi", data={"user": user})

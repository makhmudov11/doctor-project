from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from apps.users.models import SmsCode, SmsCodeTypeChoices
from apps.users.serializers import SmsCodeSerializer, ResendCodeSerializer, UserSerializer, VerifyCodeSerializer
from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.token_claim import get_tokens_for_user

User = get_user_model()


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
                    "sms_code_obj": SmsCodeSerializer(user_code_obj).data,
                    "qolgan_urinishlar_soni": self.MAX_ATTEMPTS - user_code_obj.attempts
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
                "sms_code_obj": sms_code_obj,
                "qayta_jonatish_qoldi": self.MAX_RESEND_CODE - sms_code_obj['resend_code']
            },
            message="Kod qaytadan yuborildi."
        )

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView

from apps.users.models import SmsCode
from apps.users.serializers import UserForgotPasswordSerializer, UserSerializer, UserResetPasswordSerializer
from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.generate_code import generate_code

User = get_user_model()


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

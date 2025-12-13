from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import SmsCodeTypeChoices, UserContactTypeChoices, SmsCode
from apps.users.serializers import RegisterSerializer, UserSerializer, LogoutSerializer, SmsCodeSerializer, \
    LoginSerializer
from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.generate_code import generate_code
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


class UserLogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return CustomResponse.success_response(
                message='Logout muvaffaqiyatli bajarildi'
            )
        except TokenError:
            return CustomResponse.error_response(
                message='Refresh token yaroqsiz',
                code=HTTP_400_BAD_REQUEST
            )

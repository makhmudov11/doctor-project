from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.permissions import UserDetailPermission
from apps.users.serializers import UserDetailSerializer, UserChangeRoleSerializer
from apps.utils import CustomResponse
from apps.utils.token_claim import get_tokens_for_user
from apps.utils.validates import get_valid_roles


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [UserDetailPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user


class UserSelectRoleRetrieveAPIView(APIView):
    permission_classes = [UserDetailPermission]

    def get(self, request):
        user = request.user
        return CustomResponse.success_response(
            data={
                "roles": user.roles,
                "active_role": request.auth["active_role"]
            }
        )

class UserChangeRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserChangeRoleSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data.get('role')

        user = request.user
        if role not in user.roles:
            return CustomResponse.error_response(
                message=f"Userda {role} ro'li mavjud emas"
            )

        user.active_role = role
        user.save(update_fields=['active_role'])
        token = get_tokens_for_user(user)
        return CustomResponse.success_response(
            message="Role muvaffaqiyatli o'zgartirildi",
            data={
                "active_role" : user.active_role,
                "token" : token
            }
        )


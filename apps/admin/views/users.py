from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView

from apps.admin.paginations.users import AdminUserListPagination
from apps.admin.permissions.users import AdminPermission
from apps.admin.serializers.users import AdminUserListSerializer, AdminUserCreateSerializer
User = get_user_model()

class AdminUserListAPIView(ListAPIView):
    permission_classes = [AdminPermission]
    serializer_class = AdminUserListSerializer
    pagination_class = AdminUserListPagination
    authentication_classes = [SessionAuthentication]
    queryset = User.objects.all()

    def get_queryset(self):
        qs = self.queryset
        contact = self.request.query_params.get('contact', '').strip()
        role = self.request.query_params.get('role', '').strip()
        full_name = self.request.query_params.get('full_name', '').strip()
        contact_type = self.request.query_params.get('contact_type', '').strip()
        gender = self.request.query_params.get('gender', '').strip()
        status = self.request.query_params.get('status', '').strip()
        is_staff = self.request.query_params.get('is_staff', '').strip()
        birth_date__gte = self.request.query_params.get('birth_date__gte', '').strip()
        birth_date__lte = self.request.query_params.get('birth_date__lte', '').strip()
        if contact:
            qs = qs.filter(contact__icontains=contact)
        if role:
            qs = qs.filter(active_role__icontains=role)
        if full_name:
            qs = qs.filter(full_name__icontains=full_name)
        if contact_type:
            qs = qs.filter(contact_type__icontains=contact_type)
        if gender:
            qs = qs.filter(gender__icontains=gender)
        if status:
            if status.lower() in ['true', '1']:
                qs = qs.filter(status=True)
            elif status.lower() in ['false', '0']:
                qs = qs.filter(status=False)
        if is_staff:
            if is_staff.lower() in ['true', '1']:
                qs = qs.filter(is_staff=True)
            elif is_staff.lower() in ['false', '0']:
                qs = qs.filter(is_staff=False)

        if birth_date__gte:
            qs = qs.filter(birth_date__gte=birth_date__gte)
        if birth_date__lte:
            qs = qs.filter(birth_date__lte=birth_date__lte)
        return qs


class AdminUserListCreateAPIView(ListCreateAPIView):
    authentication_classes = [SessionAuthentication]
    serializer_class = AdminUserCreateSerializer
    permission_classes = [AdminPermission]
    queryset = User.objects.all()


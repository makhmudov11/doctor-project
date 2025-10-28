from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, contact=None, password=None, **kwargs):
        user = None
        if '@' in contact:
            try:
                user = User.objects.get(email=contact)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(phon_number=contact)
            except User.DoesNotExist:
                return None

        if user and user.check_password(password):
            return user
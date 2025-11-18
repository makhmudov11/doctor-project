from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


# class EmailOrPhoneBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#
#         contact = username or kwargs.get('contact')  # admin uchun 'username', API uchun 'contact'
#         if not contact:
#             return None
#
#         user = None
#         if contact and  '@' in contact:
#             try:
#                 user = User.objects.get(cont=contact)
#             except User.DoesNotExist:
#                 return None
#         else:
#             try:
#                 user = User.objects.get(phon_number=contact)
#             except User.DoesNotExist:
#                 return None
#
#         if user and user.check_password(password):
#             return user
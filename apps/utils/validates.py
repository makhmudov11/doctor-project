import re

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def validate_email_or_phone_number(value):
    # allowed_domains = ['gmail.com', 'icloud.com', 'outlook.com', 'mail.ru', 'facebook.com']
    # email_pattern = r'^[A-Za-z0-9]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}$'
    # phone_pattern = r'^\+998\d{9}$'


    # if not re.fullmatch(email_pattern, value.strip()) and not re.fullmatch(phone_pattern, value.strip()):
    #         raise ValidationError("Email yoki telefon raqam kiriting.")

    # if re.fullmatch(email_pattern, value.strip()):
        # domain = value.strip().split('@')[-1]
        # if domain not in allowed_domains:
        #     return Response(
        #         f"{domain} domeni ruxsat etilmagan. Masalan (example123@gmail.com)",
        #          status=status.HTTP_401_UNAUTHORIZED)
    if '@' in value:
        return 'email'
    return 'phone'

import re

from rest_framework.exceptions import ValidationError


def validate_email_or_phone_number(value):
    allowed_domains = ['gmail.com', 'icloud.com', 'outlook.com', 'mail.ru', 'facebook.com']
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    phone_pattern = r'^(\+\d{12}|\d{9})$'
    if re.match(email_pattern, value):
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(
                f"{domain.upper()} domeni ruxsat etilmagan. Masalan (example123@gmail.com)")
        return 'email'
    elif re.match(phone_pattern, value):
        return 'phone_number'
    else:
        raise ValidationError({'Email yoki telefon raqam noto‘g‘ri formatda.'})

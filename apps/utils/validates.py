import re

from rest_framework.exceptions import ValidationError


def validate_email_or_phone_number(value):
    allowed_domains = ['gmail.com', 'icloud.com', 'outlook.com', 'mail.ru', 'facebook.com']

    pattern = r'^(\+\d{12}|\d{9})$'

    if '@' not in value and not re.match(pattern, value):
        raise ValidationError("Email yoki telefon kiriting")
    if '@' in value:
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(f"{domain.upper()} domeni ruxsat etilmagan. Faqat {', '.join(allowed_domains)} ishlatish mumkin.")
    if '@' in value:
        return 'email'
    return 'phone'

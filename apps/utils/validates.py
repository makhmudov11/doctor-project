import re

from apps.users.choices import CustomUserRoleChoices


def validate_email_or_phone_number(contact=''):
    EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    PHONE_NUMBER_REGEX = r'^\+998\d{9}$'

    contact = contact.strip()

    if not re.fullmatch(EMAIL_REGEX, contact) and not re.fullmatch(PHONE_NUMBER_REGEX, contact):
        return False
    if '@' in contact:
        return 'email'
    return 'phone'


def get_valid_roles():
    return {c[0] for c in CustomUserRoleChoices.choices}

import random
from django.core.cache import cache
from apps.users.tasks import send_email_task


def generate_code():
    return random.randint(100000, 999999)


def send_verification(contact):
    code = generate_code()
    cache.set(contact, code, timeout=300)  # 5 daqiqa
    send_email_task.delay(contact, code)
    return code

import random
from django.core.cache import cache
from apps.users.tasks import send_email_task
import logging
logger = logging.getLogger(__name__)


def generate_code():
    return random.randint(100000, 999999)


def send_verification(contact, data: dict):
    code = generate_code()
    cache.set(contact, {"code" : code, "data" : data}, timeout=180)  # 3 daqiqa
    try:
        send_email_task.delay(contact, code)
    except Exception as exc:
        logger.exception("Xatolik Delayda: %s", exc)
    return code

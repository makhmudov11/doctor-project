from django.core.mail import send_mail
from django.conf import settings


def send_verification_code(email, code):
    subject = "Tasdiqlash kodi"
    message = f"Sizning tasdiqlash kodingiz: {code}"

    send_mail(
        subject,
        message,
        f"Medical APP <{settings.EMAIL_HOST_USER}>",
        [email],
        fail_silently=False,
    )

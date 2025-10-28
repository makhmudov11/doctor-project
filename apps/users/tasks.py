from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_task(email, code):
    subject = "Tasdiqlash kodi"
    message = f"Sizning tasdiqlash kodingiz: {code}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
    print(f"✅ Email yuborildi: {email} → {code}")


@shared_task
def send_sms_task(phone, code):
    # Bu joyda SMS API chaqiriladi, hozircha faqat print
    print(f"📱 SMS yuborildi {phone} ga: {code}")

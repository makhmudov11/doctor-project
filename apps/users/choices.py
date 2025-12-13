from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserRoleChoices(models.TextChoices):
    SHIFOKOR = "Shifokor", _("Shifokor")
    ADMIN = "Admin", _("Admin")
    SUPERADMIN = "SuperAdmin", _("SuperAdmin")
    FOYDALANUVCHI = "FOYDALANUVCHI", _("FOYDALANUVCHI")
    KLINIKA = "Klinika", _("Klinika")
    COMPANY = "PharmCompany", _("PharmCompany")
    MEDBRAT = "MedBrat", _("MedBrat")
    MENEJER = "Menejer", _("Menejer")


class UserSocialAuthRegistrationTypeChoices(models.TextChoices):
    GOOGLE = ("google", "google")
    FACEBOOK = ("facebook", "facebook")
    APPLE = ("apple", "apple")


class UserContactTypeChoices(models.TextChoices):
    PHONE = ('phone', 'phone')
    EMAIL = ('email', 'email')


def default_roles():
    return [CustomUserRoleChoices.FOYDALANUVCHI]
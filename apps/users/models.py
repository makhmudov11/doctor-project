from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.managers import CustomUserManager
from apps.utils.base_models import CreateUpdateBaseModel


class CustomUserRoleChoices(models.TextChoices):
    SHIFOKOR = "Shifokor", _("Shifokor")
    ADMIN = "Admin", _("Admin")
    SUPERADMIN = "SuperAdmin", _("SuperAdmin")
    BEMOR = "Bemor", _("Bemor")
    KLINIKA = "Klinika", _("Klinika")
    COMPANY = "PharmCompany", _("PharmCompany")
    MEDBRAT = "MedBrat", _("MedBrat")
    MENEJER = "Menejer", _("Menejer")


class CustomUser(AbstractBaseUser, PermissionsMixin, CreateUpdateBaseModel):
    full_name = models.CharField(max_length=200)
    contact = models.CharField(max_length=200, unique=True, db_index=True)
    contact_type = models.CharField(max_length=100, null=True, blank=True)
    active_role = models.CharField(max_length=30,
                                   choices=CustomUserRoleChoices.choices,
                                   default=CustomUserRoleChoices.SHIFOKOR,
                                   null=True, blank=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'contact'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        ordering = ['-id']

    def __str__(self):
        return self.full_name or self.contact or self.contact_type

    def get_full_name(self):
        return f"{self.full_name.title()}" or self.contact


class SmsCode(CreateUpdateBaseModel):
    contact = models.CharField(max_length=255)
    hash_code = models.CharField(max_length=255)
    attempts = models.PositiveSmallIntegerField(default=1)
    verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def create_for_contact(cls, contact, hash_code, second=180):
        return cls.objects.create(
            contact=contact,
            hash_code=hash_code,
            expires_at=timezone.now() + timedelta(seconds=second)
        )

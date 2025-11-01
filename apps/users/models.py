from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
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
    email = models.EmailField(unique=True, db_index=True, null=True, blank=True)
    phone_number = models.CharField(unique=True, null=True, blank=True)
    active_role = models.CharField(max_length=30,
                                   choices=CustomUserRoleChoices.choices,
                                   default=CustomUserRoleChoices.SHIFOKOR,
                                   null=True, blank=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        ordering = ['-id']

    def __str__(self):
        return self.full_name or self.email or self.phone_number

    def get_full_name(self):
        return f"{self.full_name.title()}" or self.email
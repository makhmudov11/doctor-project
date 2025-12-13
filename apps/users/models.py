from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.users.choices import UserContactTypeChoices, UserSocialAuthRegistrationTypeChoices, CustomUserRoleChoices, \
    default_roles
from apps.users.managers import CustomUserManager
from apps.utils.base_models import  CreateUpdateBaseModel, GenderChoices
from apps.utils.generate_code import generate_public_id


class CustomUser(AbstractBaseUser, PermissionsMixin, CreateUpdateBaseModel):
    public_id = models.PositiveIntegerField(null=True, db_index=True)
    full_name = models.CharField(max_length=200, null=True)
    contact = models.CharField(max_length=200, unique=True, db_index=True)
    contact_type = models.CharField(max_length=100, null=True, choices=UserContactTypeChoices.choices)
    registration_type = models.CharField(null=True, blank=True,
                                         choices=UserSocialAuthRegistrationTypeChoices.choices
                                         )
    active_role = models.CharField(
        max_length=100,
        choices=CustomUserRoleChoices.choices,
        default=CustomUserRoleChoices.FOYDALANUVCHI,
        null=True,
        blank=True
    )
    roles = models.JSONField(default=default_roles, null=True, blank=True)
    image = models.ImageField(upload_to='users/image/', null=True, blank=True)
    birth_date = models.DateField(null=True)
    gender = models.CharField(null=True, choices=GenderChoices.choices)
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


    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = generate_public_id(CustomUser)
        super().save(*args, **kwargs)


class SmsCodeTypeChoices(models.TextChoices):
    LOGIN = 'login', 'login'
    REGISTER = 'register', 'register'
    CHANGE_PASSWORD = 'change-password', 'change password'


class SmsCode(CreateUpdateBaseModel):
    contact = models.CharField(max_length=255)
    hash_code = models.CharField(max_length=255)
    attempts = models.PositiveSmallIntegerField(default=0)
    resend_code = models.PositiveSmallIntegerField(default=1)
    verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    delete_obj = models.DateTimeField(null=True, blank=True)
    _type = models.CharField(max_length=50, null=True,
                             choices=SmsCodeTypeChoices.choices)  # login yoki register and change-password

    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def clean_verified(self):
        if self.is_expired():
            self.verified = True
            self.save()

    @classmethod
    def create_for_contact(cls, contact, hash_code, _type='', second=180):
        cls.objects.filter(
            verified=False
        ).filter(
            Q(delete_obj__lt=timezone.now()) | Q(resend_code__gte=3)
        ).delete()

        sms_code_obj = cls.objects.create(
            contact=contact,
            hash_code=hash_code,
            expires_at=timezone.now() + timedelta(seconds=second),
            delete_obj=timezone.now() + timedelta(minutes=10),
            _type=_type
        )
        return sms_code_obj

    class Meta:
        db_table = 'sms_code'
        verbose_name = 'Sms Code'
        verbose_name_plural = 'Sms Codes'

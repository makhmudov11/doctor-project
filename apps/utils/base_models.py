from django.db import models




class CreateUpdateBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class GenderChoices(models.TextChoices):
    ERKAK = 'erkak', 'erkak'
    AYOL = 'ayol', 'ayol'


class PublicIdChoice(models.TextChoices):
    USER = 'user', 'user'


class PublicIdCounter(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Public ID Counter"
        verbose_name_plural = "Public ID'S Counter"
        db_table = "public_id_counter"
        abstract = True

    def __str__(self):
        return f"{self.name} → {self.value}"

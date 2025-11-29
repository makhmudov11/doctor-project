
from django.contrib.auth import get_user_model
from apps.utils.base_models import CreateUpdateBaseModel, Gender

User = get_user_model()



# class Doctor(CreateUpdateBaseModel):
#     user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='doctor')
#     speciality = models.CharField(max_length=255)
#     exprience_year = models.PositiveSmallIntegerField(default=0)
#     working_hours = models.JSONField(default=dict, blank=True)
#     gender = models.CharField(null=True, choices=Gender.choices)
#     bio = models.TextField(null=True, blank=True)
#     qualifications = models.TextField(null=True)
#     rating = models.FloatField(default=0)
#     status = models.BooleanField(default=True)
#
#     def __str__(self) -> str:
#         if self.user:
#             return self.user.full_name or self.contact
#         return self.pk

# class Patient(CreateUpdateBaseModel):
#     user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='patient')

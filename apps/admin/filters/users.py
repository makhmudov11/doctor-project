import django_filters
from django.contrib.auth import get_user_model

User = get_user_model()


class UserListFilter(django_filters.FilterSet):
    birth_date__gte = django_filters.DateTimeFilter(field_name='birth_date', lookup_expr='gte')
    birth_date__lte = django_filters.DateTimeFilter(field_name='birth_date', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['birth_date__gte', 'birth_date__lte']

import django_filters
from apps.profile.models import Profile, Story


class UserProfileListFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    class Meta:
        model = Profile
        fields = ['created_at__gte', 'created_at__lte', 'updated_at__gte', 'updated_at__lte']



class UserStoryListFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    expires_at__gte = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_at__lte = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')


    class Meta:
        model = Story
        fields = ['created_at__gte', 'created_at__lte', 'updated_at__gte', 'updated_at__lte',
                  'expires_at__gte', 'expires_at__lte']


def get_user_active_role(user=None):
    return user.active_role
from django.urls import path

from apps.profile.views.follow_views import UserProfileFollowAPIView, UserUnFollowAPIView
from apps.profile.views.profile_views import UserProfileListAPIView, UserProfileCreateAPIView, \
    UserMyProfileRetrieveAPIView, UserMyProfileDetailRetrieveUpdateDestroyAPIView, UserProfileRetrieveAPIView
from apps.profile.views.story_views import UserStoryCreateAPIView, UserStoryListAPIView, UserActiveStoryListAPIView, \
    UserStoryMarkViewedAPIView

app_name = 'profile'

urlpatterns = [
    path('list/', UserProfileListAPIView.as_view(), name='profile-list'),
    path('create/', UserProfileCreateAPIView.as_view(), name='profile-create'),
    path('me/', UserMyProfileRetrieveAPIView.as_view(), name='my-profile'),
    path('me/detail', UserMyProfileDetailRetrieveUpdateDestroyAPIView.as_view(), name='my-profile-detail'),
    path('detail/<int:profile_public_id>', UserProfileRetrieveAPIView.as_view(), name='profile-detail-other'),
    path('story/create/', UserStoryCreateAPIView.as_view(), name='story_create'),
    path('story/list/', UserStoryListAPIView.as_view(), name='story_list'),
    path('story/active/', UserActiveStoryListAPIView.as_view(), name='story_active'),
    path('story/<int:story_public_id>/view/', UserStoryMarkViewedAPIView.as_view(), name='story_view'),
    path('<int:profile_public_id>/follow/', UserProfileFollowAPIView.as_view(), name='following'),
    path('<int:profile_public_id>/unfollow/', UserUnFollowAPIView.as_view(), name='unfollow'),

    path('followers/me', UserUnFollowAPIView.as_view(), name='followers-me'),
    path('following/me', UserUnFollowAPIView.as_view(), name='followers-me'),
    path('<int:profile_public_id>/followers/', UserUnFollowAPIView.as_view(), name='users-followers'),
    path('<int:profile_public_id>/following/', UserUnFollowAPIView.as_view(), name='users-following'),
]

from django.urls import path

from apps.profile.views import UserProfileListAPIView, UserProfileRetrieveUpdateDestroyAPIView, \
    UserStoryCreateAPIView, UserStoryListAPIView, UserActiveStoryListAPIView, UserStoryMarkViewedAPIView, \
    UserProfileFollowAPIView, UserUnFollowAPIView

app_name = 'profile'

urlpatterns = [
    path('list/', UserProfileListAPIView.as_view(), name='profile-list'),
    path('detail/<int:pk>', UserProfileRetrieveUpdateDestroyAPIView.as_view(), name='profile-detail'),
    path('story/create/', UserStoryCreateAPIView.as_view(), name='story_create'),
    path('story/list/', UserStoryListAPIView.as_view(), name='story_list'),
    path('story/active/', UserActiveStoryListAPIView.as_view(), name='story_active'),
    path('story/<int:story_id>/view/', UserStoryMarkViewedAPIView.as_view(), name='story_view'),
    path('<int:profile_id>/follow/', UserProfileFollowAPIView.as_view(), name='following'),
    path('<int:profile_id>/unfollow/', UserUnFollowAPIView.as_view(), name='unfollow'),
    # path('me/following/', UserStoryMarkViewedAPIView.as_view(), name='mark_viewed'),
    # path('me/followers/', UserStoryMarkViewedAPIView.as_view(), name='mark_viewed'),
]


from django.urls import path

from apps.profile.views import UserProfileListAPIView, UserProfileRetrieveUpdateDestroyAPIView, \
    UserStoryCreateAPIView, UserStoryListAPIView, UserActiveStoryListAPIView, UserStoryMarkViewedAPIView

app_name = 'profile'

urlpatterns = [
    path('list/', UserProfileListAPIView.as_view(), name='profile-list'),
    path('detail/<int:pk>', UserProfileRetrieveUpdateDestroyAPIView.as_view(), name='profile-detail'),
    path('story/create/', UserStoryCreateAPIView.as_view(), name='story_create'),
    path('story/list/', UserStoryListAPIView.as_view(), name='story_list'),
    path('story/active/', UserActiveStoryListAPIView.as_view(), name='story_active'),
    path('story/<int:story_id>/view/', UserStoryMarkViewedAPIView.as_view(), name='story_view'),
    # path('<int:pk>/follow/', UserStoryMarkViewedAPIView.as_view(), name='mark_viewed'),
    # path('<int:id>/unfollow/', UserStoryMarkViewedAPIView.as_view(), name='mark_viewed'),
    # path('me/following/', UserStoryMarkViewedAPIView.as_view(), name='mark_viewed'),
    # path('me/followers/', UserStoryMarkViewedAPIView.as_view(), name='mark_viewed'),
]


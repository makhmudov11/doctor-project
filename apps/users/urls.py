from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from apps.users.views import (RegisterCreateAPIView, LoginAPIView, VerifyCodeAPIView, ResendCode,
                              UserRetrieveUpdateAPIView, UserForgotPasswordAPIView, UserResetPasswordAPIView,
                              )
from apps.users.social_auth.views import (UserGoogleSocialAuthAPIView, UserFacebookSocialAuthAPIView,
                                          UserAppleSocialAuthAPIView)
app_name = 'users'

urlpatterns = [
    path('register/', RegisterCreateAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify/', VerifyCodeAPIView.as_view(), name='verify'),
    path('forgot-password/', UserForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', UserResetPasswordAPIView.as_view(), name='reset-password'),
    path('auth/social/google/', UserGoogleSocialAuthAPIView.as_view(), name='auth-social-google'),
    path('auth/social/facebook/', UserFacebookSocialAuthAPIView.as_view(), name='auth-social-facebook'),
    path('auth/social/apple/', UserAppleSocialAuthAPIView.as_view(), name='auth-social-apple'),
    path('resend/', ResendCode.as_view(), name='resend-code'),
    path('detail/', UserRetrieveUpdateAPIView.as_view(), name='user-detail'),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
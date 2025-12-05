from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

SPECTACULAR_URL = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')
]
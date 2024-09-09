from django.urls import path
from . import views

urlpatterns = [
    path('api-keys/', views.api_keys_settings, name='api_keys_settings'),
    path('use-api/', views.use_api, name='use_api'),
]
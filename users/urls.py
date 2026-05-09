from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegistrationView, ProfileView

urlpatterns = [
    # JWT токены
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Регистрация
    path('register/', RegistrationView.as_view(), name='register'),

    # Профиль
    path('profile/', ProfileView.as_view(), name='profile'),
]
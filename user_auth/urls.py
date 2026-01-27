from django.urls import path
from .views import AuthUserLogin, AuthUserRegister 

urlpatterns = [
    path('auth/login/', AuthUserLogin.as_view(), name='login'),
    path('auth/register/', AuthUserRegister.as_view(), name='register'),
]

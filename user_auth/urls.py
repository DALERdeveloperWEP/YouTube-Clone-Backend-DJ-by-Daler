from django.urls import path, include
from .views import AuthUserLogin, AuthUserRegister, AuthUserVerify, logout_view

urlpatterns = [
    path('auth/login/', AuthUserLogin.as_view(), name='login'),
    path('auth/register/', AuthUserRegister.as_view(), name='register'),
    path('auth/verify/', AuthUserVerify.as_view(), name='verify'),
    path('auth/logout/', logout_view, name='logout'),
]

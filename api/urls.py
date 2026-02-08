from django.urls import path
from .views import GetUsersUsername


urlpatterns = [
    path('api/users/username', GetUsersUsername.as_view())
]

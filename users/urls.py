from django.urls import path
from .views import Test02


urlpatterns = [
    path('', Test02.as_view())
]

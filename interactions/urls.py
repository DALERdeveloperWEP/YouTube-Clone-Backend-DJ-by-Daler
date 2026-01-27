from django.urls import path
from .views import Test01


urlpatterns = [
    path('', Test01.as_view())
]

from django.urls import path
from .views import ChannelView


urlpatterns = [
    path('channel/', ChannelView.as_view(), name='create_channel')
]

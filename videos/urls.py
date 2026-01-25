from django.urls import path
from .views import HomePage, VideoDetailPage

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('video_detail/', VideoDetailPage.as_view(), name='video_detail')
]

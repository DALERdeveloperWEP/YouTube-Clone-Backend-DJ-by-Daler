from django.urls import path
from .views import HomePage, VideoDetailPage

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('<slug:slug>/', VideoDetailPage.as_view(), name='video_detail')
]

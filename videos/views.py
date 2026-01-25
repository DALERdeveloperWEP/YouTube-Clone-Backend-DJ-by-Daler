from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views import View

class HomePage(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'index.html')


    def post(self, request: HttpRequest) -> HttpResponse:
        pass

class VideoDetailPage(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'video-detail.html')


    def post(self, request: HttpRequest) -> HttpResponse:
        pass
 


from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse


class AuthUserLogin(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'login-register.html', context={"view": 'login'})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        pass


class AuthUserRegister(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'login-register.html', context={"view": 'register'})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        pass
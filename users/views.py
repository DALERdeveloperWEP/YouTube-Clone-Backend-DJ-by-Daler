from django.shortcuts import render
from django.views import View
from django.http import  HttpRequest, HttpResponse

class Test02(View):
    def get(request: HttpRequest) ->HttpResponse:
        pass
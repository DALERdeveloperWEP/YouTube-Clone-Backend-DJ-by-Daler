from uuid import uuid4

from django.shortcuts import render, redirect
from django.views import View
from django.http import  HttpRequest, HttpResponse, JsonResponse
from .models import Channel
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import boto3
from django.conf import settings

from decouple import config

@method_decorator(login_required, name='dispatch')
class ChannelView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render
    
    def post(self, request: HttpRequest) -> HttpResponse:
        
        logo_public_url = None
        banner_public_url = None
        
        ALLOWED_IMAGE_TYPES = [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
            "image/svg+xml"
        ]


        name=request.POST.get('name')
        description=request.POST.get('description', '')
        avatar=request.FILES.get('avatar')
        banner=request.FILES.get('banner')
    
        
        if not name:
            return render(request, 'index.html', context={"Errors": "name berish majburiy"})
    
        if avatar and avatar.content_type not in ALLOWED_IMAGE_TYPES:
            return JsonResponse({"error": "Avatar faqat rasm bo‘lishi kerak"}, status=400)

        if banner and banner.content_type not in ALLOWED_IMAGE_TYPES:
            return JsonResponse({"error": "Banner faqat rasm bo‘lishi kerak"}, status=400)
        
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )
        
        user = request.user
        
        
        if avatar:
            avatar_path = f"{user.username}/logo/{str(uuid4())}.{avatar.content_type.split('/')[-1]}"
                
            try:
                s3.upload_fileobj(
                    avatar,
                    settings.R2_BUCKET_NAME,
                    avatar_path,
                    ExtraArgs={"ContentType": avatar.content_type},
                )
                logo_public_url = f"{config('DEV_PUBLICK_URL')}/{avatar_path}"
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        
        if banner:
            banner_path = f"{user.username}/banner/{str(uuid4())}.{banner.content_type.split('/')[-1]}"
           
            try:
                s3.upload_fileobj(
                    banner,
                    settings.R2_BUCKET_NAME,
                    banner_path,
                    ExtraArgs={"ContentType": banner.content_type},
                )
                banner_public_url = f"{config('DEV_PUBLICK_URL')}/{banner_path}"
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        
        channel = Channel.objects.create(
            user=request.user,
            name=name,
            description=description,
        )
        
        updated = False

        if avatar:
            channel.avatar = logo_public_url
            updated = True

        if banner:
            channel.banner = banner_public_url
            updated = True

        if updated:
            channel.save()
        
        return redirect('home')
    




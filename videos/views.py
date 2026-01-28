from uuid import uuid4
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decouple import config
from django.contrib.auth import get_user_model
import boto3
from django.conf import settings
from moviepy import VideoFileClip

from .models import Video, Category
from users.models import Channel


User = get_user_model()


def get_video_duration(file_path_or_url):
    clip = VideoFileClip(file_path_or_url)
    seconds = int(round(clip.duration))
    clip.reader.close()  # video readerni yopish
    # audio readerni xavfsiz yopish
    if clip.audio and hasattr(clip.audio.reader, 'close_proc'):
        clip.audio.reader.close_proc()
    return seconds


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02}:{secs:02}"
    return f"{minutes}:{secs:02}"



def get_videos_home_page():
    videos = []
    get_videos = Video.objects.all()    
    for video in get_videos:
        user_channel = Channel.objects.filter(user=video.user).first()
        videos.append({
            "title": video.title,
            "description": video.description,
            "public_url": video.public_url,
            "channel_name": user_channel.name,
            "channel_logo": user_channel.avatar,
            "uploaded_at": video.uploaded_at,
            "views": video.views,
            "duration": video.duration,
        })
    return videos


def get_video_detail(slug: str):
    get_videos = Video.objects.filter(slug=slug)
    user_channel = Channel.objects.filter(user=get_videos.user.id)
    video = {
        "title": get_videos.title,
        "description": get_videos.description,
        "public_url": get_videos.public_url,
        "channel_name": user_channel.name,
        "channel_logo": user_channel.avatar,
        "uploaded_at": get_videos.uploaded_at,
        "views": get_videos.views,
        "category": get_videos.category,
    }

    return video



@method_decorator(csrf_exempt, name='dispatch')
class HomePage(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'index.html', context={"videos": get_videos_home_page()})


    def post(self, request: HttpRequest) -> JsonResponse:
        
        if not request.user.is_authenticated:
            return redirect("login")
        
        ALLOWED_VIDEO_TYPES = [
            "video/mp4",
            "video/mkv",
            "video/webm",
            "video/avi",
            "video/mov",
        ]

        ALLOWED_IMAGE_TYPES = [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
            "image/svg+xml"
        ]
        user = User.objects.filter(id=2).first()
        video = request.FILES.get("video")
        thumbnail = request.FILES.get('thumbnail')
        title = request.POST.get('title')
        description = request.POST.get('description')
        # category = request.body.get('category')
        categories = [
            'Development',
            'Code'
        ]
        
        if not title and not  description and not categories:
            return JsonResponse({'Erros': "Bad Request"}, status=400)
        
        if not video:
            return JsonResponse({"error": "Video topilmadi"}, status=400)

        if video.content_type not in ALLOWED_VIDEO_TYPES:
            return JsonResponse({"error": "Faqat video fayl ruxsat etiladi"}, status=400)
        
        if not thumbnail:
            return JsonResponse({"error": "thumbnail topilmadi"}, status=400)
        
        if thumbnail.content_type not in ALLOWED_IMAGE_TYPES:
            return JsonResponse(
                {"error": "Faqat rasm (image) fayllar ruxsat etiladi"},
                status=400
            )
            
            
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )
        

        video_path = f"{user.username}/videos/{str(uuid4())}.{video.content_type.split('/')[-1]}"
        thumbnail_path = f"{user.username}/thumbnail/{str(uuid4())}.{thumbnail.content_type.split('/')[-1]}"
        existing_categories = Category.objects.filter(name__in=categories)
        
        
        if len(list(existing_categories)) == 0:
            return JsonResponse({"Erros": "Category not found."}, status=404)

        try:
            s3.upload_fileobj(
                video,
                settings.R2_BUCKET_NAME,
                video_path,
                ExtraArgs={"ContentType": video.content_type},
            )
            s3.upload_fileobj(
                thumbnail,
                settings.R2_BUCKET_NAME,
                thumbnail_path,
                ExtraArgs={"ContentType": thumbnail.content_type},
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        public_url = f"{config('DEV_PUBLICK_URL')}/{video_path}"
        thumbnail_public_url = f"{config('DEV_PUBLICK_URL')}/{thumbnail_path}"
        
        duration_seconds = get_video_duration(public_url)  # moviepy ishlaydi
        duration = format_duration(duration_seconds)
        
        
        save_video = Video(
            title=title,
            description=description,
            public_url=public_url,
            thumbnail=thumbnail_public_url,
            user=user,
            duration=duration,
        )
        save_video.save()
        save_video.category.set(existing_categories)
    
        existing_category_names = list(existing_categories.values_list('name', flat=True))
        result = {}
        for cat in categories:
            result[cat] = "save successful" if cat in existing_category_names else "not found"
        
        return render(request, 'index.html', context=get_videos_home_page())


class VideoDetailPage(View):
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        return render(request, 'watch.html')


    def post(self, request: HttpRequest) -> HttpResponse:
        pass
 


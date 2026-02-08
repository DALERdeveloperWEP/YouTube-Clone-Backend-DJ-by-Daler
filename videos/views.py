import json
from uuid import uuid4
from django.shortcuts import render, redirect
from django.urls import reverse
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
from users.models import Channel, Subscriber
from interactions.models import Reaction, Comment


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
            "slug": video.slug,
            "description": video.description,
            "thumbnail": video.thumbnail,
            "channel_name": user_channel.name,
            "channel_logo": user_channel.avatar,
            "uploaded_at": video.uploaded_at,
            "views": video.views,
            "duration": video.duration,
        })
    return videos


def get_video_detail(slug: str):
    get_video = Video.objects.filter(slug=slug).first()
    user_channel = Channel.objects.filter(user=get_video.user.id).first()
    total_like = Reaction.objects.filter(video=get_video, position='like').count()
    video = {
        "title": get_video.title,
        "description": get_video.description,
        "public_url": get_video.public_url,
        "thumbnail": get_video.thumbnail,
        "channel_name": user_channel.name,
        "channel_logo": user_channel.avatar,
        "uploaded_at": get_video.uploaded_at,
        "views": get_video.views,
        "category": get_video.category,
        "total_subscribers": Subscriber.objects.filter(channel=user_channel).count(),
        'total_like': total_like
    }

    return video



@method_decorator(csrf_exempt, name='dispatch')
class HomePage(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        
        all_categories = [category.name for category in Category.objects.all()]
        
        if request.user.is_authenticated:
            get_user_channel = Channel.objects.filter(user=request.user).first()
        else:
            get_user_channel = Channel.objects.none()  # bo'sh QuerySet
        
        
        return render(request, 'index.html', context={
            "videos": get_videos_home_page(), 
            "categories": all_categories, 
            "user": request.user,
            "channel": get_user_channel,
        })


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
        user = request.user
        video = request.FILES.get("video")
        thumbnail = request.FILES.get('thumbnail')
        title = request.POST.get('title')
        description = request.POST.get('description')
        raw = request.POST.get("categories")
        categories = json.loads(raw) if raw else []
        
        print(categories)
        
        if not title or not categories:
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
        existing_categories = Category.objects.filter(name__in=categories)
        if len(list(existing_categories)) == 0:
            return JsonResponse({"Erros": "Category not found."}, status=404)
            
        
        

        video_path = f"{user.username}/videos/{str(uuid4())}.{video.content_type.split('/')[-1]}"
        thumbnail_path = f"{user.username}/thumbnail/{str(uuid4())}.{thumbnail.content_type.split('/')[-1]}"
        
        
        print(1)

        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name="auto",
            )
            s3.upload_fileobj(
                video,
                settings.R2_BUCKET_NAME,
                video_path,
                ExtraArgs={"ContentType": video.content_type},
            )
            print(3)
            s3.upload_fileobj(
                thumbnail,
                settings.R2_BUCKET_NAME,
                thumbnail_path,
                ExtraArgs={"ContentType": thumbnail.content_type},
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        print(3)
        public_url = f"{config('DEV_PUBLICK_URL')}/{video_path}"
        thumbnail_public_url = f"{config('DEV_PUBLICK_URL')}/{thumbnail_path}"
        duration_seconds = get_video_duration(public_url) 
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
        
        all_categories = [category.name for category in Category.objects.all()]
        
        if request.user.is_authenticated:
            get_user_channel = Channel.objects.filter(user=request.user).first()
        else:
            get_user_channel = Channel.objects.none()  # bo'sh QuerySet
        
        
        
        return JsonResponse({"message": "Video created successfully"}, status=201)
    
@method_decorator(csrf_exempt, name='dispatch')
class VideoDetailPage(View):
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        video_detail = get_video_detail(slug)
        video = Video.objects.filter(slug=slug).first()
        if request.user.is_authenticated:
            print('xa 1')
            user_reaction = Reaction.objects.filter(user=request.user, video=video).exists()
            if user_reaction:
                print('xa 2')
                user_reaction_get_position = Reaction.objects.filter(user=request.user, video=video).first()
            else:
                user_reaction_get_position = None
            user_subscribe = Subscriber.objects.filter(subscriber=request.user, channel=video.user.channel).exists()
        else:
            user_reaction = False
            user_subscribe = False
            user_reaction_get_position = False
        
        all_comments = Comment.objects.filter(video=video, parent__isnull=True).select_related("user").order_by("-created_at")
            
            
        return render(request, 'watch.html', context={
            'video': video_detail, 
            'user_subscriber': user_subscribe,
            'user_reaction': user_reaction,
            'user_reaction_position': user_reaction_get_position,
            'comments': all_comments,
        })


    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        user = request.user
        video = Video.objects.filter(slug=slug).first()
        print('bosh')
        if not user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
        if not video:
            return JsonResponse({"error": "Video not found."}, status=404)
        try:
            to_channel_subscribe = video.user.channel
        except Channel.DoesNotExist:
            return JsonResponse({"error": "Channel not found for the user."}, status=404)
        if request.user.is_authenticated:
            print('xa')
            dataAction = json.loads(request.body.decode()).get('action')
            dataReaction = json.loads(request.body.decode()).get('reaction')
        else:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
        commentContent = json.loads(request.body.decode("utf-8")).get('content')  # Comment content
        
        # Comment qo'shish
        if commentContent:
            new_comment = Comment.objects.create(
                video=video,
                user=user,
                content=commentContent
            )
            return JsonResponse({
                "message": "Comment added successfully.",
                "comment": {
                    "id": new_comment.id,
                    "content": new_comment.content,
                    "username": user.username,
                    "created_at": new_comment.created_at.isoformat(),
                }
            }, status=201)
        
        match dataAction:
            case 'subscribe':
                if not user.is_authenticated:
                    return JsonResponse({"error": "Authentication required."}, status=401)
                if Subscriber.objects.filter(subscriber=user, channel=to_channel_subscribe).exists():
                    return JsonResponse({"error": "Already subscribed."}, status=400)
                new_subscriber = Subscriber(subscriber=user, channel=to_channel_subscribe)
                new_subscriber.save()
                return JsonResponse({"message": "Subscribed successfully."}, status=201)
                
            case 'unsubscribe':
                get_subscription = Subscriber.objects.filter(subscriber=user, channel=to_channel_subscribe)
                if get_subscription.exists():
                    get_subscription.delete()
                    return JsonResponse({"message": "Unsubscribed successfully."}, status=200)
                return JsonResponse({"error": "Subscription not found."}, status=404)
                                
            
        match dataReaction:
            
            case 'like':
                if not user.is_authenticated:
                    return JsonResponse({"error": "Authentication required."}, status=401)
                dislike_exist_reaction = Reaction.objects.filter(video=video, user=user, position='dislike')
                if dislike_exist_reaction.exists():
                    dislike_exist_reaction.delete()
                new_reaction = Reaction(video=video, user=user, position='like')
                new_reaction.save()
                return JsonResponse({"message": "Liked successfully."}, status=201)
            
            case 'removelike':
                exist_reaction= Reaction.objects.filter(video=video, user=user, position='like')
                if exist_reaction.exists():
                    exist_reaction.delete()
                    return JsonResponse({"message": "Like removed successfully."}, status=200)
                return JsonResponse({"error": "Like reaction not found."}, status=404)
            
            
            case 'dislike':
                if not user.is_authenticated:
                    return JsonResponse({"error": "Authentication required."}, status=401)
                if Reaction.objects.filter(video=video, user=user, position='dislike').exists():
                    return JsonResponse({"error": "Already disliked."}, status=400)
                like_exist_reaction = Reaction.objects.filter(video=video, user=user, position='like')
                if like_exist_reaction.exists():
                    like_exist_reaction.delete()
                new_reaction = Reaction(video=video, user=user, position='dislike')
                new_reaction.save()
                return JsonResponse({"message": "Disliked successfully."}, status=201)
            
            case 'removedislike':
                exist_reaction= Reaction.objects.filter(video=video, user=user, position='dislike')
                if exist_reaction.exists():
                    exist_reaction.delete()
                    return JsonResponse({"message": "Dislike removed successfully."}, status=200)
                return JsonResponse({"error": "Dislike reaction not found."}, status=404)
                        
        return render(request, 'watch.html')
 
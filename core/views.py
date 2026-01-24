# views.py

import boto3
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render

ALLOWED_VIDEO_TYPES = [
    "video/mp4",
    "video/mkv",
    "video/webm",
    "video/avi",
    "video/mov",
]

def upload_video_r2(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    video = request.FILES.get("video")
    if not video:
        return JsonResponse({"error": "Video topilmadi"}, status=400)

    if video.content_type not in ALLOWED_VIDEO_TYPES:
        return JsonResponse({"error": "Faqat video fayl ruxsat etiladi"}, status=400)

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    file_key = f"videos/{video.name}"

    try:
        s3.upload_fileobj(
            video,
            settings.R2_BUCKET_NAME,
            file_key,
            ExtraArgs={"ContentType": video.content_type},
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    file_url = f"{settings.R2_ENDPOINT_URL}/{settings.R2_BUCKET_NAME}/{file_key}"

    return JsonResponse({
        "success": True,
        "file": file_key,
        "url": file_url
    })

def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'test.html')

def get_video_url(request, filename):
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.R2_BUCKET_NAME,
            "Key": f"videos/{filename}",
        },
        ExpiresIn=300  # 5 daqiqa
    )

    return JsonResponse({"url": url})

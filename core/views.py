from uuid import uuid4
import boto3
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth import get_user_model
from decouple import config
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from moviepy import VideoFileClip

from videos.models import Video, Category
# import subprocess
# import json


User = get_user_model()

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

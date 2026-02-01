from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from moviepy import VideoFileClip


User = get_user_model()


def get_video_duration(url: str) -> str:
    """
    Public URL'dan video duration olish va YouTube style (M:SS / H:MM:SS) formatga o'tkazish
    """
    clip = VideoFileClip(url)
    seconds = int(round(clip.duration))
    clip.reader.close()
    clip.audio.reader.close_proc() if clip.audio else None

    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02}:{secs:02}"
    return f"{minutes}:{secs:02}"


class Category(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name


class Video(models.Model):
    title = models.CharField(max_length=127)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=500, blank=True)
    public_url = models.URLField()
    thumbnail = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    category = models.ManyToManyField(Category)
    duration = models.CharField(max_length=8, blank=True)
    
    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(self.title)[:25]
            
            counter = 1
            while Video.objects.filter(slug=self.slug).exists():
                self.slug = f'{self.title}-{counter}'
                counter+=1
                
        if not self.duration and self.public_url:
            try:
                self.duration = get_video_duration(self.public_url)
            except Exception as e:
                print(f"Cannot get duration: {e}")
                self.duration = "0:00"
        
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title    

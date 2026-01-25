from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=64)


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
    duration = models.CharField(max_length=8)
    
    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(self.title)
            
            counter = 1
            while Video.objects.filter(slug=self.slug).exists():
                self.slug = f'{self.title}-{counter}'
                counter+=1
        
        return super().save(*args, **kwargs)    





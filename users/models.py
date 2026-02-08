from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Channel(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=1000, blank=True)
    avatar = models.URLField(blank=True, default='https://i.pinimg.com/originals/9f/16/72/9f1672710cba6bcb0dfd93201c6d4c00.jpg')
    banner = models.URLField(blank=True, default='https://preview.redd.it/jn8jyih8obj71.jpg?width=1060&format=pjpg&auto=webp&s=00093bf1491726eea4a752290353e0e169522b66')
    subscribers_count  = models.PositiveIntegerField(blank=True, default=0)
    total_videos = models.PositiveIntegerField(blank=True, default=0)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    


class Subscriber(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="subscribers")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('subscriber', 'channel')
        ordering = ['-subscribed_at']
        
    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.channel.name}"
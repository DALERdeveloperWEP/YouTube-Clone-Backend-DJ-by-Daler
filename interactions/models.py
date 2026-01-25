from django.db import models
from django.contrib.auth import get_user_model

from videos.models import Video


User = get_user_model()


class Comment(models.Model):
    video = models.ForeignKey(Video, related_name='video_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_comments', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subcomments', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.user.username} comment on {self.video.title}"


class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    
    video = models.ForeignKey(Video, related_name='video_reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_reactions', on_delete=models.CASCADE)
    position = models.CharField(choices=REACTION_CHOICES, max_length=10, default=LIKE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {self.position}d {self.video.title}"
    


class History(models.Model):
    user = models.ForeignKey(User, related_name='history', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, related_name='watched_history', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"



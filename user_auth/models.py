from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emailotp')
    code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"
    
from django import template
from django.utils import timezone
from datetime import timedelta


register = template.Library()


@register.filter
def yt_ago(value):
    if not value:
        return ""
    now = timezone.now()
    diff = now - value
    
    if diff < timedelta(minutes=1):
        return "just now"
    if diff < timedelta(hours=1):
        m = diff.seconds // 60
        return f"{m} minute{'s' if m != 1 else ''} ago"
    if diff < timedelta(days=1):
        h = diff.seconds // 3600
        return f"{h} hour{'s' if h != 1 else ''} ago"
    if diff < timedelta(weeks=1):
        d = diff.days
        return f"{d} day{'s' if d != 1 else ''} ago"
    w = diff.days // 7
    return f"{w} week{'s' if w != 1 else ''} ago"
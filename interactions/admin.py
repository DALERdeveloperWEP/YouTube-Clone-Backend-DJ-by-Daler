from django.contrib import admin
from .models import Reaction, Comment, History

admin.site.register(Reaction)
admin.site.register(Comment)
admin.site.register(History)
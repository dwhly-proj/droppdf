from django.urls import path, re_path

from .views import *

urlpatterns = [
        re_path(r'video/(?P<video_id>.+)/$', youtube_video,
            name='youtube_video'),
        ]

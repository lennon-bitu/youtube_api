from django.urls import path
from . import views

urlpatterns = [
    path("download/", views.download_video),
    path("info/", views.video_info),
    path("health/", views.health),
]
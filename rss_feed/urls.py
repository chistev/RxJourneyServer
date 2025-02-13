from django.urls import path
from .feeds import LatestPostsFeed

urlpatterns = [
    path('rss/', LatestPostsFeed(), name='rss_feed'),
]

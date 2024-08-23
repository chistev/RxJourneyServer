from django.urls import path
from .views import random_posts

urlpatterns = [
    path('random-posts/<slug:slug>/', random_posts, name='random-posts'),
]

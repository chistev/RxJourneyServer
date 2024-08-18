from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    comment_count = models.PositiveIntegerField(default=0)  # Renamed field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()


class Subscriber(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} subscribed on {self.subscribed_at}'
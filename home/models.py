from django.db import models
from django.utils.html import strip_tags
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from home.email_services import send_post_notification
import re


class Post(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    content = CKEditor5Field('Text', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_excerpt(self, char_limit=300):
        # Return the first 'char_limit' characters of the raw HTML content
        if len(self.content) > char_limit:
            return self.content[:char_limit] + "..."
        return self.content

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            post_excerpt = self.get_excerpt()
            send_post_notification(self.title, post_excerpt, self.slug)

    def __str__(self):
        return self.title


class Subscriber(models.Model):
    email = models.EmailField(unique=True, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} subscribed on {self.subscribed_at}'

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

    def get_excerpt(self, word_limit=100):
        # Strip HTML tags from content
        plain_text_content = strip_tags(self.content)

        # Replace HTML entities like &nbsp; with a space
        plain_text_content = plain_text_content.replace('&nbsp;', ' ')

        # Split the content into words
        words = re.findall(r'\b\w+\b', plain_text_content)

        # Limit the number of words
        truncated_words = words[:word_limit]

        # Join words back into a string and add ellipsis if truncated
        truncated_content = ' '.join(truncated_words)
        return f"{truncated_content}..." if len(words) > word_limit else truncated_content

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            post_excerpt = self.get_excerpt()
            subject = f"New Post: {self.title}"
            send_post_notification(subject, self.title, post_excerpt, self.slug)

    def __str__(self):
        return self.title


class Subscriber(models.Model):
    email = models.EmailField(unique=True, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} subscribed on {self.subscribed_at}'

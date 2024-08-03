from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure email is unique
    full_name = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Ensure full_name is unique

    def __str__(self):
        return self.email

class EmailConfirmationToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=2)

    def __str__(self):
        return self.email

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
User = get_user_model()  # This will get the default User model or your custom user model if configured
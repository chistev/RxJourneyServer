from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

User = get_user_model()  # This will get the default User model or your custom user model if configured


@login_required()
def check_admin_status(request):
    user = request.user
    return JsonResponse({
        'is_admin': user.is_admin,
        'is_authenticated': user.is_authenticated,
        'username': user.username,
    })

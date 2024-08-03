import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.utils.decorators import method_decorator

from my_auth.models import EmailConfirmationToken, CustomUser


@method_decorator(csrf_exempt, name='dispatch')
class ValidateTokenView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            token_instance = EmailConfirmationToken.objects.filter(token=token).first()
            if token_instance and not token_instance.is_expired():
                return JsonResponse({'valid': True, 'data': {'email': token_instance.email}, 'message': 'Token is valid'})
            else:
                return JsonResponse({'valid': False, 'message': 'Token is invalid or expired'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CreateAccountView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = escape(data.get('email'))
        full_name = escape(data.get('fullName'))
        password = data.get('password')
        token = escape(data.get('token'))

        if not full_name or len(full_name) < 5:
            return JsonResponse({'success': False, 'message': 'Full name must be at least 5 characters long.'})

        if not password or len(password) < 8:
            return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters long.'})

        try:
            email_token = EmailConfirmationToken.objects.get(email=email, token=token)
            if email_token.is_expired():
                return JsonResponse({'success': False, 'message': 'Token expired.'})
        except EmailConfirmationToken.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid token.'})

        try:
            user = CustomUser.objects.create_user(username=full_name, email=email, password=password)
            email_token.delete()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({'success': True})
        except IntegrityError as e:
            # Handle specific integrity errors related to unique constraints
            if 'unique constraint' in str(e):
                # Check if the error is related to email or username
                if 'email' in str(e):
                    return JsonResponse({'success': False, 'message': 'Email already registered.'})
                elif 'username' in str(e):
                    return JsonResponse({'success': False, 'message': 'Full name already taken.'})
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again.'})
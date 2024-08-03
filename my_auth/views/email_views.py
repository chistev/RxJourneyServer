import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from my_auth.models import CustomUser, EmailConfirmationToken
from my_auth.utils.email_utils import send_confirmation_email


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CheckEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()

            try:
                validate_email(email)
            except ValidationError:
                print(f'Invalid email format: {email}')
                return JsonResponse({'exists': False, 'error': 'Invalid email format'}, status=400)

            email_exists = CustomUser.objects.filter(email=email).exists()
            if email_exists:
                return JsonResponse({'exists': True})

            token = get_random_string(length=32)
            EmailConfirmationToken.objects.create(email=email, token=token)
            send_confirmation_email(email, token)

            return JsonResponse({'exists': False, 'message': 'Confirmation email sent'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            return JsonResponse({'error': 'Internal server error'}, status=500)

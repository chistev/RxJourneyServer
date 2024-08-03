from django.http import JsonResponse
from django.views import View
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
import requests
import os
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, EmailConfirmationToken
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.html import escape
User = get_user_model()  # This will get the default User model or your custom user model if configured


def send_confirmation_email(email, token):
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephenowabie@gmail.com'
    sender_name = 'Chistev'

    # Define the email content
    subject = "Complete Your Registration"
    html_content = f"""
    <p>RxJourney</p>
    <p>Your login link</p>
    <p>Click the link below to confirm your email and finish creating your RxJourney account.<br>
    This link will expire in 2 hours and can only be used once.</p>
    <p><a href="http://localhost:5173/confirm-email?token={token}">Create your account</a></p>
    <p>If the button above doesn’t work, paste this link into your web browser:<br>
    http://localhost:5173/confirm-email?token={token}</p>
    """

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'api-key': api_key
    }

    response = requests.post(api_url, data=json.dumps(payload), headers=headers)

    if response.status_code == 201:
        print("Confirmation email sent successfully.")
    else:
        print(f"Failed to send confirmation email. Response: {response.text}")


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCsrfToken(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE', '')})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CheckEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()

            # Validate the email format
            try:
                validate_email(email)
            except ValidationError:
                print(f'Invalid email format: {email}')
                return JsonResponse({'exists': False, 'error': 'Invalid email format'}, status=400)

            # Check if the email exists
            email_exists = User.objects.filter(email=email).exists()
            if email_exists:
                return JsonResponse({'exists': True})

            # Generate a token for email confirmation
            token = get_random_string(length=32)

            # Save the token and email
            token_instance = EmailConfirmationToken.objects.create(email=email, token=token)
            print(f'Token created and saved: {token_instance.token} for email: {token_instance.email}')

            # Send confirmation email
            send_confirmation_email(email, token)

            return JsonResponse({'exists': False, 'message': 'Confirmation email sent'})
        except json.JSONDecodeError:
            print('Invalid JSON received')
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ValidateTokenView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            token_instance = EmailConfirmationToken.objects.filter(token=token).first()
            if token_instance and not token_instance.is_expired():
                # Include email in the response
                return JsonResponse({'valid': True, 'data': {'email': token_instance.email}, 'message': 'Token is valid'})
            else:
                return JsonResponse({'valid': False, 'message': 'Token is invalid or expired'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CreateAccountView(View):
    def post(self, request):
        print("Received a request to create an account")

        data = json.loads(request.body)
        email = escape(data.get('email'))
        full_name = escape(data.get('fullName'))
        password = data.get('password')
        token = escape(data.get('token'))

        print(f"Received data - Email: {email}, Full Name: {full_name}, Token: {token}, Password: {password}")

        # Validation
        if not full_name or len(full_name) < 5:
            print("Full name validation failed")
            return JsonResponse({'success': False, 'message': 'Full name must be at least 5 characters long.'})

        if not password or len(password) < 8:
            print("Password validation failed")
            return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters long.'})

        # Check if email or full_name is already taken
        if CustomUser.objects.filter(email=email).exists():
            print("Email already registered")
            return JsonResponse({'success': False, 'message': 'Email already registered.'})

        if CustomUser.objects.filter(full_name=full_name).exists():
            print("Full name already taken")
            return JsonResponse({'success': False, 'message': 'Full name already taken.'})

        try:
            email_token = EmailConfirmationToken.objects.get(email=email, token=token)
            if email_token.is_expired():
                print("Token has expired")
                return JsonResponse({'success': False, 'message': 'Token expired.'})
        except EmailConfirmationToken.DoesNotExist:
            print("Token does not exist")
            return JsonResponse({'success': False, 'message': 'Invalid token.'})

        print("All validations passed, creating the user")

        # Create the user
        user = CustomUser.objects.create_user(username=full_name, email=email, password=password)
        email_token.delete()

        print(f"User created with email: {user.email}")

        # Authenticate the user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"User {user.email} logged in successfully")

        return JsonResponse({'success': True})
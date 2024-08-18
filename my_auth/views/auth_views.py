import json
import re

from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
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


def validate_email(email):
    """Validate email format."""
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email) is not None


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        print("Received a POST request.")
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            print(f"Parsed data: {data}")

            email = data.get('email', '').strip()  # Strip leading/trailing whitespace from email
            password = data.get('password', '')  # Do not strip password
            print(f"Email: {email}")
            print(f"Password: {'*' * len(password) if password else 'Not provided'}")

            # Validate email format
            if not validate_email(email):
                print("Invalid email format.")
                return JsonResponse({'error': 'Invalid email format.'}, status=400)

            # Validate that email and password are not empty
            if not email or not password:
                print("Email or password is empty.")
                return JsonResponse({'error': 'Email and password are required.'}, status=400)

            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                print("User authenticated successfully.")

                # User is authenticated, log them in to create a session
                login(request, user)

                # Get the session key from the request
                session_key = request.session.session_key
                print(f"Session key: {session_key}")

                # Create a response and set the session key in a cookie
                response = JsonResponse({'success': 'Authenticated successfully.'})
                response.set_cookie('sessionid', session_key, httponly=True, secure=False)

                return response
            else:
                print("Invalid email or password.")
                # Do not specify whether email or password is incorrect
                return JsonResponse({'error': 'Invalid email or password.'}, status=400)
        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return JsonResponse({'error': 'Invalid request format.'}, status=400)
        except Exception as e:
            # Log unexpected errors for debugging
            print(f'Unexpected error: {e}')
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)


@csrf_exempt
def sign_out_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import JsonResponse
from .models import Subscriber


def validate_email_address(email):
    try:
        validate_email(email)
        return True, ""
    except ValidationError:
        return False, "Invalid email format"


def check_email_exists(email):
    return Subscriber.objects.filter(email=email).exists()

def confirm_subscription(token):
    signer = TimestampSigner()
    try:
        email = signer.unsign(token, max_age=3600)

        if not Subscriber.objects.filter(email=email).exists():
            Subscriber.objects.create(email=email)
            return JsonResponse({'valid': True, 'message': 'Subscription confirmed and saved!'}, status=200)
        else:
            return JsonResponse({'valid': True, 'message': 'Subscription already confirmed.'}, status=200)

    except (BadSignature, SignatureExpired):
        return JsonResponse({'valid': False, 'message': 'Invalid or expired token'}, status=400)

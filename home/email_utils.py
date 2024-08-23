import json
import os
import requests
from django.core.signing import TimestampSigner


def generate_confirmation_token(email):
    signer = TimestampSigner()
    return signer.sign(email)


def send_confirmation_email(email, token):
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephenowabie@gmail.com'
    sender_name = 'Chistev'

    subject = "Confirm Your Subscription"
    html_content = f"""
    <p>Hello,</p>
    <p>Please click the link below to confirm your subscription.<br>
    This link will expire in 1 hour.</p>
    <p><a href="http://localhost:5173/confirm-email?token={token}">Confirm Subscription</a></p>
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

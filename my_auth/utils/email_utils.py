import os
import json
import requests


def send_confirmation_email(email, token):
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephenowabie@gmail.com'
    sender_name = 'Chistev'

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

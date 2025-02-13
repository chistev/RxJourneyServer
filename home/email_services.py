import json
import os
import requests

def send_post_notification(subject, post_title, post_excerpt, post_slug):
    from .models import Subscriber

    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephenowabie@gmail.com'
    sender_name = 'Chistev'

    subscribers = Subscriber.objects.all()
    recipient_emails = [subscriber.email for subscriber in subscribers]

    for email in recipient_emails:
        message = f"""
        <html>
        <body>
            <p>Hello,</p>
            <p>We have a new post on our blog!<br><br>
            <strong>{post_title}</strong></p>
            <p>{post_excerpt}</p>
            <p><a href="https://rxjourney.com.ng/{post_slug}">Read more</a></p>
        </body>
        </html>
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
            "htmlContent": message
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': api_key
        }

        response = requests.post(api_url, data=json.dumps(payload), headers=headers)

        if response.status_code == 201:
            print(f"Notification email sent successfully to {email}.")
        else:
            print(f"Failed to send notification email to {email}. Response: {response.text}")

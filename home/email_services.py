import os
import json
import requests
from .models import Subscriber, UnsubscribeToken


def send_post_notification(post_title, post_slug):
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephen@rxjourney.net'
    sender_name = 'Chistev'
    reply_to_email = 'chistev12@gmail.com'

    subject = f"New Post: {post_title}"

    subscribers = Subscriber.objects.all()
    recipient_emails = [subscriber.email for subscriber in subscribers]

    for email in recipient_emails:
        token = UnsubscribeToken.objects.create(email=email)
        unsubscribe_link = f"https://rxjourneyserver.pythonanywhere.com/home/unsubscribe?token={token.token}"
        post_link = f"https://rxjourney.net/{post_slug}"

        html_content = f"""
        <p>Hello,</p>
        <p>We have a new post on our blog:</p>
        <p><strong>{post_title}</strong></p>
        <p><a href="{post_link}">Read the full post here</a></p>
        <p>If you no longer wish to receive these notifications, <a href="{unsubscribe_link}">unsubscribe here</a>.</p>
        <p>Thank you,<br>Chistev</p>
        """

        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email,
            },
            "replyTo": {
                "email": reply_to_email
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
            print(f"✅ Notification email sent successfully to {email}.")
        else:
            print(f"❌ Failed to send notification email to {email}. Response: {response.text}")
            
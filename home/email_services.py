import os
import requests

def send_post_notification(post_title, post_excerpt, post_slug):
    from .models import Subscriber, UnsubscribeToken

    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephenowabie@gmail.com'
    sender_name = 'Chistev'
    brevo_template_id = 12

    subscribers = Subscriber.objects.all()
    recipient_emails = [subscriber.email for subscriber in subscribers]

    for email in recipient_emails:
        token = UnsubscribeToken.objects.create(email=email)
        unsubscribe_link = f"https://rxjourneyserver.pythonanywhere.com/home/unsubscribe?token={token.token}"
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
            "templateId": brevo_template_id,
            "params": {
                "title": post_title,
                "excerpt": post_excerpt,
                "slug": post_slug,
                "unsubscribe_link": unsubscribe_link
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': api_key
        }

        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 201:
            print(f"✅ Notification email sent successfully to {email}.")
        else:
            print(f"❌ Failed to send notification email to {email}. Response: {response.text}")

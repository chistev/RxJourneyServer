import json
import os

import requests
from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.validators import validate_email
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from my_auth.models import CustomUser
from .models import Post, Subscriber
from .serializers import PostSerializer
from .permissions import IsAdminUser


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check for existing post with the same title
            if Post.objects.filter(title=serializer.validated_data['title']).exists():
                return Response({'error': 'A post with this title already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({'success': True}, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class SubscriberCountView(APIView):
    def get(self, request, *args, **kwargs):
        subscriber_count = Subscriber.objects.count()
        return Response({'subscriber_count': subscriber_count}, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({'message': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        if Subscriber.objects.filter(email=email).exists():
            return Response({'message': 'Email already subscribed'}, status=status.HTTP_200_OK)

        # Create a confirmation token
        signer = TimestampSigner()
        token = signer.sign(email)

        # Send confirmation email
        self.send_confirmation_email(email, token)

        return Response({
            'message': 'A confirmation email has been sent. Please check your inbox to confirm your subscription.',
            'expires_in': '1 hour'
        }, status=status.HTTP_200_OK)

    def send_confirmation_email(self, email, token):
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

    def confirm_subscription(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        if not token:
            return Response({'message': 'Invalid or missing token'}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        try:
            # Verify token and check expiration (1 hour)
            email = signer.unsign(token, max_age=3600)
            Subscriber.objects.create(email=email)
            return Response({'message': 'Subscription confirmed'}, status=status.HTTP_201_CREATED)
        except (BadSignature, SignatureExpired):
            return Response({'message': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class UnsubscribeView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        subscriber = Subscriber.objects.filter(user=user).first()
        if subscriber:
            subscriber.delete()
            return Response({'message': 'Unsubscribed successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Not subscribed'}, status=status.HTTP_400_BAD_REQUEST)


class CheckSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        is_subscribed = Subscriber.objects.filter(user=user).exists()
        return Response({'is_subscribed': is_subscribed})


class SearchResultsView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        else:
            posts = Post.objects.all()

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

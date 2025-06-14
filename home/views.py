from django.db.models import Q
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Post, Subscriber, UnsubscribeToken
from .serializers import PostSerializer
from .email_utils import generate_confirmation_token, send_confirmation_email
from .subscriptions import validate_email_address, check_email_exists, confirm_subscription

from django.shortcuts import redirect
from django.views import View

import requests
import os


class PostPagination(PageNumberPagination):
    page_size = 10  # Return 10 posts per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = PostPagination

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
        recaptcha_token = request.data.get('recaptcha_token')

        recaptcha_secret = os.environ.get('RECAPTCHA_SECRET_KEY')

        recaptcha_response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': recaptcha_secret,
                'response': recaptcha_token
            }
        )
        result = recaptcha_response.json()

        if not result.get('success') or result.get('score', 0) < 0.5:
            return Response({'message': 'reCAPTCHA verification failed'}, status=status.HTTP_400_BAD_REQUEST)


        # Validate email format
        is_valid, error_message = validate_email_address(email)
        if not is_valid:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        if check_email_exists(email):
            return Response({'message': 'Email already subscribed'}, status=status.HTTP_200_OK)

        # Create a confirmation token and send email
        token = generate_confirmation_token(email)
        send_confirmation_email(email, token)

        return Response({
            'message': 'A confirmation email has been sent. Please check your inbox to confirm your subscription.',
            'expires_in': '1 hour'
        }, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')
        if not token:
            return JsonResponse({'valid': False, 'message': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        return confirm_subscription(token)


class UnsubscribeView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        subscriber = Subscriber.objects.filter(user=user).first()
        if subscriber:
            subscriber.delete()
            return Response({'message': 'Unsubscribed successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Not subscribed'}, status=status.HTTP_400_BAD_REQUEST)
    

class HandleUnsubscribeView(View):
    def get(self, request):
        token_value = request.GET.get('token')
        if not token_value:
            return redirect('https://rxjourney.net/unsubscribe/invalid')

        try:
            token = UnsubscribeToken.objects.get(token=token_value)
        except UnsubscribeToken.DoesNotExist:
            return redirect('https://rxjourney.net/unsubscribe/invalid')

        if token.is_expired():
            return redirect('https://rxjourney.net/unsubscribe/expired')

        if token.unsubscribed:
            return redirect('https://rxjourney.net/unsubscribe/already')

        Subscriber.objects.filter(email=token.email).delete()
        token.unsubscribed = True
        token.save()

        return redirect('https://rxjourney.net/unsubscribe/success')


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

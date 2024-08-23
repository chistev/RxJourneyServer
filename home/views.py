from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Post, Subscriber
from .serializers import PostSerializer
from .email_utils import generate_confirmation_token, send_confirmation_email
from .subscriptions import validate_email_address, check_email_exists, confirm_subscription


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

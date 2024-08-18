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
        user = request.user
        if not Subscriber.objects.filter(user=user).exists():
            Subscriber.objects.create(user=user)
            return Response({'message': 'Subscribed successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already subscribed'}, status=status.HTTP_200_OK)


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
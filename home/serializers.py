from rest_framework import serializers

from detail.models import Comment
from home.models import Post, Subscriber


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'username', 'content', 'created_at', 'parent', 'replies']

    def get_replies(self, obj):
        # Recursively serialize the child comments (replies)
        if obj.replies.exists():
            serialized_data = CommentSerializer(obj.replies.all(), many=True).data
            print(serialized_data)  # Print serialized data for debugging
            return serialized_data
        return []


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'image', 'slug', 'content', 'created_at']


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['id', 'email', 'subscribed_at']
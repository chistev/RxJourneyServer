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
    comments = CommentSerializer(many=True, read_only=True)
    total_likes = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'image', 'slug', 'content', 'created_at', 'total_likes', 'comments', 'liked']

    def get_total_likes(self, obj):
        return obj.total_likes

    def get_liked(self, obj):
        request = self.context.get('request')
        return request.user in obj.likes.all()


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['id', 'user', 'subscribed_at']

import json
import random

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods

from detail.models import Comment
from home.models import Post


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({'liked': liked, 'total_likes': post.likes.count()})


from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from .models import Post, Comment

@require_POST
def add_comment(request):
    try:
        data = json.loads(request.body)
        post_id = data.get('postId')
        content = data.get('content')
        parent_id = data.get('parentId')

        post = Post.objects.get(id=post_id)
        user = request.user

        parent_comment = Comment.objects.get(id=parent_id) if parent_id else None

        comment = Comment.objects.create(
            post=post,
            user=user,
            content=content,
            parent=parent_comment
        )

        return JsonResponse({'status': 'success', 'commentId': comment.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def get_comments(request, post_id):
    order = request.GET.get('order', 'most-relevant')

    if order == 'newest':
        comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
    elif order == 'oldest':
        comments = Comment.objects.filter(post_id=post_id).order_by('created_at')
    else:
        comments = Comment.objects.filter(post_id=post_id).order_by('created_at')

    def get_replies(parent_comment_id):
        replies = Comment.objects.filter(parent_id=parent_comment_id).order_by('created_at')
        return [
            {
                'id': reply.id,
                'username': reply.user.username,
                'avatar': 'bi-person',  # You can customize this
                'time': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'text': reply.content,
                'replies': get_replies(reply.id),  # Recursively fetch replies
            }
            for reply in replies
        ]

    comment_list = [
        {
            'id': comment.id,
            'username': comment.user.username,
            'avatar': 'bi-person',  # You can customize this
            'time': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'text': comment.content,
            'replies': get_replies(comment.id),  # Fetch replies for each comment
        }
        for comment in comments
    ]

    return JsonResponse({'comments': comment_list})


@login_required
@require_http_methods(["DELETE"])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)

        if comment.replies.exists():
            # Option 1: Mark as deleted and keep child comments
            comment.content = "[Deleted]"
            comment.save()
        else:
            # Option 2: Fully delete if no replies
            comment.delete()

        return JsonResponse({'status': 'success'})
    except Comment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Comment not found or not owned by you'}, status=404)


def edit_comment(request, comment_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            comment = Comment.objects.get(id=comment_id)
            comment.content = content
            comment.save()
            return JsonResponse({'status': 'success'})
        except Comment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Comment not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def random_posts(request, slug):
    # Get the current post
    current_post = get_object_or_404(Post, slug=slug)

    # Fetch all posts excluding the current one
    other_posts = Post.objects.exclude(id=current_post.id)

    # Shuffle the posts and select up to 4
    random_posts = random.sample(list(other_posts), min(len(other_posts), 4))

    # Prepare the response data
    response_data = [
        {
            'title': post.title,
            'slug': post.slug,
            'image': post.image.url if post.image else None,
            'created_at': post.created_at,
            'content': post.content[:300] + '...',  # Trim content for preview
            'likes': post.total_likes,
            'comments': post.comment_count,
        }
        for post in random_posts
    ]

    return JsonResponse(response_data, safe=False)
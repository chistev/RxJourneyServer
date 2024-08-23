import random
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from home.models import Post


def random_posts(request, slug):
    current_post = get_object_or_404(Post, slug=slug)

    other_posts = Post.objects.exclude(id=current_post.id)

    # Shuffle the posts and select up to 4
    random_posts = random.sample(list(other_posts), min(len(other_posts), 4))

    response_data = [
        {
            'title': post.title,
            'slug': post.slug,
            'created_at': post.created_at,
            'content': post.content[:300] + '...',  # Trim content for preview
        }
        for post in random_posts
    ]

    return JsonResponse(response_data, safe=False)

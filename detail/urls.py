from django.urls import path
from .views import toggle_like, add_comment, get_comments, delete_comment, edit_comment, random_posts

urlpatterns = [
    path('toggle-like/<int:post_id>/', toggle_like, name='toggle-like'),
    path('add-comment/', add_comment, name='add_comment'),
    path('comments/<int:post_id>/', get_comments, name='get_comments'),
    path('delete-comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('edit-comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('random-posts/<slug:slug>/', random_posts, name='random-posts'),
]

from django.urls import path
from .views import PostCreateView, PostListView, PostDetailView, SubscriberCountView, SubscribeView, UnsubscribeView, \
    CheckSubscriptionView, SearchResultsView

urlpatterns = [
    path('posts/', PostCreateView.as_view(), name='create-post'),
    path('post_list/', PostListView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('subscriber-count/', SubscriberCountView.as_view(), name='subscriber-count'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('check-subscription/', CheckSubscriptionView.as_view(), name='check-subscription'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
]

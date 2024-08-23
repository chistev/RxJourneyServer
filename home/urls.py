from django.urls import path
from .views import PostListView, PostDetailView, SubscriberCountView, SubscribeView, UnsubscribeView, \
    SearchResultsView

urlpatterns = [
    path('post_list/', PostListView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('subscriber-count/', SubscriberCountView.as_view(), name='subscriber-count'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('validate-token/', SubscribeView.as_view(), name='validate-token'),
]

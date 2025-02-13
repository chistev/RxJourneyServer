from django.contrib.syndication.views import Feed

from home.models import Post


class LatestPostsFeed(Feed):
    title = "RXJOURNEY BLOG POSTS"
    link = "/rss_feed/rss/"
    description = "Updates on new blog posts"

    def items(self):
        return Post.objects.all().order_by('-created_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.get_excerpt()

    def item_link(self, item):
        return f'https://rxjourney.com.ng/{item.slug}/'

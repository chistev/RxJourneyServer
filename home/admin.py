from django.contrib import admin
from .models import Post, Subscriber, UnsubscribeToken


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_at',)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)


@admin.register(UnsubscribeToken)
class UnsubscribeTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created_at', 'unsubscribed')
    search_fields = ('email', 'token')
    list_filter = ('unsubscribed', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(unsubscribed=True)
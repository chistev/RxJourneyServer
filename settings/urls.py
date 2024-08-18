from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import UserDetailView, DeleteAccountView, SignOutSessionsView, ChangePasswordView

urlpatterns = [
    path('api/user/', UserDetailView.as_view(), name='user-detail'),
    path('api/delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    path('sign-out-sessions/', SignOutSessionsView.as_view(), name='sign-out-sessions'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
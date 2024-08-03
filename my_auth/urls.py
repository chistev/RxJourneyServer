# your_app/urls.py

from django.urls import path
from .views.csrf_views import GetCsrfToken
from .views.email_views import CheckEmailView
from .views.auth_views import ValidateTokenView, CreateAccountView

urlpatterns = [
    path('get-csrf-token/', GetCsrfToken.as_view(), name='get_csrf_token'),
    path('check-email/', CheckEmailView.as_view(), name='check_email'),
    path('validate-token/<str:token>/', ValidateTokenView.as_view(), name='validate_token'),
    path('create-account', CreateAccountView.as_view(), name='create_account'),
]

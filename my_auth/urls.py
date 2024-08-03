from django.urls import path
from .views import CheckEmailView, CreateAccountView, GetCsrfToken, ValidateTokenView

urlpatterns = [
    path('get-csrf-token/', GetCsrfToken.as_view(), name='get_csrf_token'),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('validate-token/<str:token>/', ValidateTokenView.as_view(), name='validate-token'),
    path('create-account', CreateAccountView.as_view(), name='create-account'),
]

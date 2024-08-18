from django.urls import path

from .views.admin_views import check_admin_status
from .views.csrf_views import GetCsrfToken
from .views.email_views import CheckEmailView
from .views.auth_views import ValidateTokenView, CreateAccountView, LoginView, sign_out_view

urlpatterns = [
    path('get-csrf-token/', GetCsrfToken.as_view(), name='get_csrf_token'),
    path('check-email/', CheckEmailView.as_view(), name='check_email'),
    path('validate-token/<str:token>/', ValidateTokenView.as_view(), name='validate_token'),
    path('create-account', CreateAccountView.as_view(), name='create_account'),
    path('check-admin-status/', check_admin_status, name='check_admin_status'),
    path('login/', LoginView.as_view(), name='login'),
    path('signout/', sign_out_view, name='signout'),
]

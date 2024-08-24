from django.urls import path
from .views.csrf_views import GetCsrfToken

urlpatterns = [
    path('get-csrf-token/', GetCsrfToken.as_view(), name='get_csrf_token'),
]

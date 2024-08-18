from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomUserSerializer

from django.contrib.auth import get_user_model, update_session_auth_hash

User = get_user_model()


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        try:
            email = request.user.email

            user = User.objects.get(email=email)
            user.delete()

            return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignOutSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the current user's session
        current_session_key = request.session.session_key

        # Invalidate all sessions except the current one
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in sessions:
            data = session.get_decoded()
            if data.get('_auth_user_id') == str(request.user.id) and session.session_key != current_session_key:
                session.delete()

        return Response({'message': 'Signed out of all other sessions successfully.'}, status=200)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Check if the current password is correct
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the new password
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({'errors': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Set and save the new password
        user.set_password(new_password)
        user.save()

        # Update session to prevent logout
        update_session_auth_hash(request, user)

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
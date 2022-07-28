from rest_framework import generics, status
from rest_framework.response import Response

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode

from .serializers import (UserSerializer,
                          UserPasswordUpdateSerializer,
                          PasswordResetRequestSerializer,
                          SetNewPasswordSerializer
                          )


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    """Get user details view"""
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user


class UserUpdatePassword(generics.UpdateAPIView):
    """Change user password view"""
    serializer_class = UserPasswordUpdateSerializer

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully'
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    """Password reset request view"""
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {'success': 'We have sent you an email with instructions for resetting your password.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    """Setting new password view"""
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        """Tell user that password reset link is available"""

        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=user_id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response(
                {'failed': 'The token has expired.'},
                status=status.HTTP_200_OK
            )
        return Response({'success': 'Enter your new password'})

    def patch(self, request, uidb64, token):
        """Change password"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {'success': 'Password has been reset successfully.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

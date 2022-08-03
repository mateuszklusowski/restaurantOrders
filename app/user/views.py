from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .serializers import (UserSerializer,
                          UserPasswordUpdateSerializer,
                          PasswordResetRequestSerializer
                          )


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


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
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {'success': 'We have sent you an email with instructions for resetting your password.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('restaurant:restaurant-list')

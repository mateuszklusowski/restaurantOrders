from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from rest_framework import serializers

from .tasks import send_reset_password_email


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""

        return get_user_model().objects.create_user(**validated_data)


class UserPasswordUpdateSerializer(serializers.Serializer):
    """Serializer for updating user password"""
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )

    class Meta:
        model = get_user_model()
        extra_kwargs = {
            'old_password': {'write_only': True, 'min_length': 5},
            'new_password': {'write_only': True, 'min_length': 5}
        }

    def validate(self, data):
        """Check that old password is correct"""
        user = self.context.get('request').user
        is_different = bool(data['new_password'] != data['old_password'])
        if not user.check_password(data['old_password']) or not is_different:
            msg = _('Old password is incorrect or similar to new one')
            raise serializers.ValidationError(msg, code='password')
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()

    class Meta:
        fields = '__all__'

    def validate(self, attrs):
        """Check that user exists"""
        email = attrs.get('email')

        if get_user_model().objects.filter(email=email).exists():
            user = get_user_model().objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(self.context.get('request')).domain
            relative_url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absolute_url = 'http://{}{}'.format(current_site, relative_url)
            email_message = 'Here is your password reset link:\n{}'.format(absolute_url)
            send_reset_password_email.delay(
                'Password reset link',
                email_message,
                user.email
            )

        else:
            msg = _('No user with this email address exists')
            raise serializers.ValidationError({'email error': msg}, code='email')

        return attrs

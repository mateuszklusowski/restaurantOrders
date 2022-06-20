from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings

from rest_framework import serializers


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


class AuthTokenSerializer(serializers.Serializer):
    """Serialzier for the user authenticaton object"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


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
            send_mail(
                subject='Reset your password',
                message=email_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email]
            )
        else:
            msg = _('No user with this email address exists')
            raise serializers.ValidationError(msg, code='email')

        return attrs


class SetNewPasswordSerializer(serializers.Serializer):
    """Serializer for setting new password"""
    new_password1 = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )
    new_password2 = serializers.CharField(
        style={'input_type': 'password'},
        required=True
    )

    class Meta:
        extra_kwargs = {
            'new_password1': {'write_only': True, 'min_length': 5},
            'new_password2': {'write_only': True, 'min_length': 5}
        }

    def validate(self, attrs):
        """Validate passwords and check token availability"""
        uidb64 = self.context.get('request').path.split('/')[-3]
        token = self.context.get('request').path.split('/')[-2]
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=user_id)

        if user:
            if not PasswordResetTokenGenerator().check_token(user, token):
                msg = _('Invalid token or expired')
                raise serializers.ValidationError({'token': msg}, code='token')

            if attrs.get('new_password1') != attrs.get('new_password2'):
                msg = _('Passwords do not match')
                raise serializers.ValidationError({'password': msg}, code='password')

            if user.check_password(attrs.get('new_password1')):
                msg = _('New password is similar to old one')
                raise serializers.ValidationError({'password': msg}, code='password')

            user.set_password(attrs.get('new_password1'))
            user.save()

            return (user)

        else:
            msg = _('Invalid token or expired')
            raise serializers.ValidationError({'token': msg}, code='token')

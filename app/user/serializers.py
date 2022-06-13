from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

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

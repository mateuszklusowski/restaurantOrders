from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.test import APIClient
from rest_framework import status

from user.tasks import send_reset_password_email

from time import sleep

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:create-token')
ME_URL = reverse('user:user-detail')
PASSWORD_CHANGE = reverse('user:change-password')
PASSWORD_RESET_URL = reverse('user:reset-password')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more that 5 characters"""
        payload = {
            'email': 'test@test.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@test.com', password='testpass')
        payload = {
            'email': 'test@test.com',
            'password': 'wrong'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that token is not created if email and password are missing"""
        res = self.client.post(TOKEN_URL, {'email': 'some', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpassword',
            name='test user'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_change_password(self):
        """Test changing the password for authenticated user"""
        payload = {
            'old_password': 'testpassword',
            'new_password': 'newpassword123'
        }
        res = self.client.patch(PASSWORD_CHANGE, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['new_password']))

    def test_change_password_with_wrong_old_password(self):
        """Test that password is not changed if the old password is wrong"""
        payload = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }

        res = self.client.patch(PASSWORD_CHANGE, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user.check_password('testpassword'))

    def test_change_password_with_similar_new_password(self):
        """Test that password is not changed if the new password is similar"""
        payload = {
            'old_password': 'testpassword',
            'new_password': 'testpassword'
        }

        res = self.client.patch(PASSWORD_CHANGE, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user.check_password('testpassword'))

    def test_reset_password_sending_mail(self):
        """Test requesting a password reset"""

        res = send_reset_password_email.delay(
            'test subject',
            'test body',
            'test@test.com'
        )
        sleep(10)
        self.assertEqual(res.status, 'SUCCESS')

    def test_reset_password_request_with_invalid_email(self):
        """Test requesting a password reset with invalid email"""
        payload = {'email': ''}

        res = self.client.post(PASSWORD_RESET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_new_password(self):
        """Test setting a new password with reset token"""
        payload = {
            'new_password1': 'testpass123',
            'new_password2': 'testpass123'
        }

        token = PasswordResetTokenGenerator().make_token(self.user)
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.pk))
        url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        res = self.client.patch(url, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['new_password1']))

    def test_set_new_password_with_invalid_credientials(self):
        """Test setting a new password with invalid credientals"""
        payload = {
            'new_password1': 'testpass123',
            'new_password2': 'wrongpassword'
        }

        token = PasswordResetTokenGenerator().make_token(self.user)
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.pk))
        url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        res = self.client.patch(url, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.check_password(payload['new_password1']))

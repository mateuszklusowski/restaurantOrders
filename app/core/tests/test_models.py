from django.test import TestCase
from django.contrib.auth import get_user_model
# from core import models


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@test.com'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalized_email(self):
        """Test the email for a new user is normalized"""
        email = 'test@TEST.com'
        user = get_user_model().objects.create_user(
            email,
            'testpassword'
        )
        self.assertEqual(user.email, email.lower())

    def test_invalid_email(self):
        """Test creating user with invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpassword')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        super_user = get_user_model().objects.create_superuser(
            'test@test.com',
            'testpassword'
        )

        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)

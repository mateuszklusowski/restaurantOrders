from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@test.com',
            'testadminpassword'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testuserpassword'
        )

    def test_users_listed(self):
        """Test that our users are listed"""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test that create user page works"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_delete_page(self):
        """Test that user delete page works"""
        url = reverse('admin:core_user_delete', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

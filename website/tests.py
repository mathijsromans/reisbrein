from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client

from reisbrein.auth import create_and_login_anonymous_user, get_anonymous_group


class TestCaseAdminLogin(TestCase):
    """Test case with client and login as admin function."""
    admin_password = '38dsiha49sd'

    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(username='admin', email='admin@test.com', password=cls.admin_password)

    def setUp(self):
        self.client = Client()
        self.login()

    def login(self):
        """Login as admin."""
        success = self.client.login(username='admin', password=self.admin_password)
        self.assertTrue(success)
        response = self.client.get('/admin/', follow=True)
        self.assertEqual(response.status_code, 200)
        return response


class TestAdminPages(TestCaseAdminLogin):

    def test_admin_homepage(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


class TestAuthentication(TestCase):

    def setUp(self):
        self.client = Client()

    def test_create_anonymous_user_on_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        users = User.objects.filter(groups=get_anonymous_group())
        self.assertTrue(users.exists())
        user = users.first()
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.usertravelpreferences is not None)

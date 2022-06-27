from accounts.models import User
from django.test import TestCase
from tests.mocks import user_info


class T1ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_info = user_info()

    def test_if_user_can_be_created(self):
        User.objects.create_user(**self.user_info)
        user: User = User.objects.all().first()
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, self.user_info["email"])
        self.assertEqual(user.first_name, self.user_info["first_name"])
        self.assertEqual(user.last_name, self.user_info["last_name"])

    def test_if_superuser_can_be_created_correctly(self):
        User.objects.create_superuser(**self.user_info)
        superuser: User = User.objects.all().first()
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.email, self.user_info["email"])
        self.assertEqual(superuser.first_name, self.user_info["first_name"])
        self.assertEqual(superuser.last_name, self.user_info["last_name"])

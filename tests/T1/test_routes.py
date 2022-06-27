from accounts.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from tests.mocks import (
    required_fields_in_request_register_critic,
    required_fields_in_response_register_critic,
    user_info,
)


class T1RouteTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_url = "http://localhost:8000/api/"
        cls.user_info = user_info()

    def test_if_critic_can_be_created(self):
        response = self.client.post(
            f"{self.base_url}users/register/", self.user_info, format="json"
        )
        critic: User = User.objects.get(id=response.json()["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            len(response.json().keys()),
            len(required_fields_in_response_register_critic()),
        )
        for field in required_fields_in_response_register_critic():
            self.assertIn(field, response.json())
        self.assertEqual(response.json()["email"], critic.email)
        self.assertEqual(response.json()["first_name"], critic.first_name)
        self.assertEqual(response.json()["last_name"], critic.last_name)

    def test_if_critic_cant_be_created_if_is_missing_fields(self):
        response = self.client.post(
            f"{self.base_url}users/register/", {}, format="json"
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in required_fields_in_request_register_critic():
            self.assertIn(field, response.json())
            self.assertEqual(response.json()[field], ["This field is required."])

    def test_if_user_can_be_created_if_its_email_is_already_in_use(self):
        self.client.post(
            f"{self.base_url}users/register/", self.user_info, format="json"
        )
        response = self.client.post(
            f"{self.base_url}users/register/", self.user_info, format="json"
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())
        self.assertEqual(response.json()["email"], ["email already exists"])

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user_default_role(self):
        user = User.objects.create_user(username="student", email="s@test.com", password="123")
        self.assertEqual(user.role, "student")
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_teacher)

    def test_create_teacher(self):
        user = User.objects.create_user(
            username="teacher", email="t@test.com", password="123", role="teacher"
        )
        self.assertEqual(user.role, "teacher")
        self.assertTrue(user.is_teacher)

    def test_create_admin(self):
        user = User.objects.create_user(
            username="admin", email="a@test.com", password="123", role="admin"
        )
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_admin)

    def test_user_str(self):
        user = User.objects.create_user(
            username="john", email="j@test.com", password="123", first_name="John"
        )
        self.assertIn("John", str(user))

    def test_unique_email(self):
        User.objects.create_user(username="u1", email="same@test.com", password="123")
        with self.assertRaises(Exception):
            User.objects.create_user(username="u2", email="same@test.com", password="123")


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="TestPass123!"
        )

    def test_get_token(self):
        response = self.client.post(
            "/api/auth/token/", {"username": "testuser", "password": "TestPass123!"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_login(self):
        response = self.client.post(
            "/api/auth/token/", {"username": "testuser", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "NewPass123!",
                "password2": "NewPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_password_mismatch(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "Pass1",
                "password2": "Pass2",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile(self):
        response = self.client.post(
            "/api/auth/token/", {"username": "testuser", "password": "TestPass123!"}, format="json"
        )
        token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token(self):
        response = self.client.post(
            "/api/auth/token/", {"username": "testuser", "password": "TestPass123!"}, format="json"
        )
        refresh = response.data["refresh"]

        response = self.client.post("/api/auth/token/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

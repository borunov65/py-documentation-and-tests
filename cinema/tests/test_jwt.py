from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse


MOVIE_URL = reverse("cinema:movie-list")
TOKEN_URL = reverse("token_obtain_pair")
TOKEN_REFRESH_URL = reverse("token_refresh")
TOKEN_VERIFY_URL = reverse("token_verify")


class JWTAuthTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )

    def test_obtain_jwt_token(self):
        """POST valid credentials to obtain JWT access and refresh tokens"""
        payload = {"email": "test@test.com", "password": "testpassword"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        self.access_token = res.data["access"]
        self.refresh_token = res.data["refresh"]

    def test_access_protected_endpoint_with_jwt(self):
        """Use obtained JWT access token to access a protected endpoint"""
        payload = {"email": "test@test.com", "password": "testpassword"}
        res = self.client.post(TOKEN_URL, payload)
        access_token = res.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        res = self.client.get(MOVIE_URL)  # приклад захищеного ендпоінта
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])

    def test_refresh_jwt_token(self):
        """POST refresh token to obtain a new access token"""
        payload = {"email": "test@test.com", "password": "testpassword"}
        res = self.client.post(TOKEN_URL, payload)
        refresh_token = res.data["refresh"]

        res = self.client.post(TOKEN_REFRESH_URL, {"refresh": refresh_token})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_verify_jwt_token(self):
        """Verify a valid JWT token"""
        payload = {"email": "test@test.com", "password": "testpassword"}
        res = self.client.post(TOKEN_URL, payload)
        access_token = res.data["access"]

        res = self.client.post(TOKEN_VERIFY_URL, {"token": access_token})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from cinema.views import MovieViewSet
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.urls import reverse

MOVIE_URL = reverse("cinema:movie-list")

class ThrottlingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    @override_settings(REST_FRAMEWORK={
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {"anon": "10/min", "user": "30/min"},
    })
    def test_anonymous_throttle(self):
        """Anonymous users: 10 requests/min"""
        original_permissions = MovieViewSet.permission_classes
        MovieViewSet.permission_classes = [AllowAny]

        for i in range(10):
            res = self.client.get(MOVIE_URL)
            self.assertEqual(res.status_code, 200)

        res = self.client.get(MOVIE_URL)
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        MovieViewSet.permission_classes = original_permissions

    @override_settings(REST_FRAMEWORK={
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {"anon": "10/min", "user": "30/min"},
    })
    def test_authenticated_throttle(self):
        """Authenticated users: 30 requests/min"""
        self.client.force_authenticate(self.user)

        for i in range(30):
            res = self.client.get(MOVIE_URL)
            self.assertEqual(res.status_code, 200)

        res = self.client.get(MOVIE_URL)
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

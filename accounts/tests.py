from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ResidentRegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse("register")
        self.data = {
            "first_name": "Ava",
            "last_name": "Santos",
            "email": "ava@example.com",
            "username": "avasantos",
            "password1": "Mango-River!274",
            "password2": "Mango-River!274",
            "address": "12 Mabini Street",
        }

    def register(self, **changes):
        return self.client.post(self.url, {**self.data, **changes})

    def test_success_creates_hashed_user_and_resident_profile_then_redirects(self):
        response = self.register()
        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="avasantos")
        self.assertEqual(user.first_name, "Ava")
        self.assertEqual(user.last_name, "Santos")
        self.assertTrue(user.check_password(self.data["password1"]))
        self.assertNotEqual(user.password, self.data["password1"])
        self.assertEqual(Profile.objects.get(user=user).address, "12 Mabini Street")
        self.assertEqual(user.profile.role, "resident")

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username="avasantos", password="another-pass-321")
        response = self.register()
        self.assertContains(response, "username is already in use")
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email_is_case_insensitive(self):
        User.objects.create_user(username="existing", email="Ava@Example.com", password="another-pass-321")
        response = self.register(email="ava@example.com")
        self.assertContains(response, "email address already exists")
        self.assertEqual(User.objects.count(), 1)

    def test_password_mismatch_is_rejected(self):
        response = self.register(password2="Different-River!274")
        self.assertContains(response, "passwords do not match")
        self.assertEqual(User.objects.count(), 0)

    def test_role_escalation_input_is_ignored(self):
        response = self.register(role="official")
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(Profile.objects.get().role, "resident")

    def test_missing_required_fields_are_reported(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_password_validation_is_enforced(self):
        response = self.register(password1="123", password2="123")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too short")
        self.assertEqual(User.objects.count(), 0)

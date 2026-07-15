from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from facilities.models import Facility

User = get_user_model()


class PublicPagesSmokeTest(TestCase):
    """Every public page should render without a server error."""

    def setUp(self):
        user = User.objects.create_user(username='doc', password='pass1234', user_type='hospital')
        Facility.objects.create(
            admin=user, name='Test Hospital', facility_type='hospital',
            address='1 Test Rd', state='Lagos', lga='Ikeja', phone='08000000000',
            is_verified=True, is_active=True,
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        response = self.client.get(reverse('facility_search'), {'state': 'Lagos'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hospital')

    def test_leaderboard_page(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hospital')

    def test_signup_page(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_request_create_requires_login(self):
        response = self.client.get(reverse('request_create'))
        self.assertEqual(response.status_code, 302)

    def test_facility_register_requires_login(self):
        response = self.client.get(reverse('facility_register'))
        self.assertEqual(response.status_code, 302)

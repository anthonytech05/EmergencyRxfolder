from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import BloodStock

from .models import Facility

User = get_user_model()


class FacilityDashboardTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='fadmin', password='pass1234', user_type='hospital')
        self.facility = Facility.objects.create(
            admin=self.admin, name='Enugu General', facility_type='hospital',
            address='3 Hospital Rd', state='Enugu', lga='Enugu East', phone='08033333333',
            is_verified=True, is_active=True,
        )
        BloodStock.objects.create(facility=self.facility, blood_type='A+', units_available=3)
        self.client.login(username='fadmin', password='pass1234')

    def test_dashboard_loads(self):
        response = self.client.get(reverse('facility_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enugu General')

    def test_profile_loads_and_updates(self):
        response = self.client.post(reverse('facility_profile'), {
            'name': 'Enugu General Hospital', 'facility_type': 'hospital',
            'address': '3 Hospital Rd', 'state': 'Enugu', 'lga': 'Enugu East',
            'phone': '08033333333', 'email': '', 'website': '',
        })
        self.assertEqual(response.status_code, 302)
        self.facility.refresh_from_db()
        self.assertEqual(self.facility.name, 'Enugu General Hospital')

    def test_requests_page_loads(self):
        response = self.client.get(reverse('facility_requests'))
        self.assertEqual(response.status_code, 200)

    def test_inventory_page_loads(self):
        response = self.client.get(reverse('inventory_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A+')

    def test_register_redirects_existing_facility_to_dashboard(self):
        response = self.client.get(reverse('facility_register'))
        self.assertRedirects(response, reverse('facility_dashboard'))

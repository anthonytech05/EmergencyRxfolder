from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from facilities.models import Facility
from inventory.models import BloodStock, MedicalSupply
from notifications.models import Notification

from .models import BroadcastLog, EmergencyRequest

User = get_user_model()


class EmergencyRequestFlowTest(TestCase):
    """End-to-end: submit a request, get broadcast to a matching facility, facility confirms."""

    def setUp(self):
        self.hospital_admin = User.objects.create_user(
            username='hospitaladmin', password='pass1234', user_type='hospital'
        )
        self.facility = Facility.objects.create(
            admin=self.hospital_admin, name='Lagos Blood Bank', facility_type='blood_bank',
            address='2 Bank Rd', state='Lagos', lga='Ikeja', phone='08011111111',
            is_verified=True, is_active=True,
        )
        BloodStock.objects.create(facility=self.facility, blood_type='O+', units_available=5)

        self.requester = User.objects.create_user(
            username='patient', password='pass1234', user_type='public', phone_number='08022222222'
        )

    def test_request_is_broadcast_to_matching_facility(self):
        self.client.login(username='patient', password='pass1234')
        response = self.client.post(reverse('request_create'), {
            'request_type': 'blood',
            'blood_type': 'O+',
            'units_needed': 2,
            'supply_name': '',
            'description': '',
            'location_text': 'Ikeja',
            'state': 'Lagos',
            'lga': 'Ikeja',
            'urgency': 'urgent',
        })
        self.assertEqual(response.status_code, 302)

        emergency_request = EmergencyRequest.objects.get()
        self.assertEqual(emergency_request.status, 'broadcasting')
        self.assertTrue(BroadcastLog.objects.filter(request=emergency_request, facility=self.facility).exists())

    def test_facility_confirming_fulfils_request(self):
        emergency_request = EmergencyRequest.objects.create(
            requester=self.requester, request_type='blood', blood_type='O+', units_needed=1,
            location_text='Ikeja', state='Lagos', lga='Ikeja',
        )
        broadcast = BroadcastLog.objects.create(request=emergency_request, facility=self.facility)

        self.client.login(username='hospitaladmin', password='pass1234')
        response = self.client.post(reverse('facility_respond', args=[broadcast.id]), {'decision': 'available'})
        self.assertEqual(response.status_code, 302)

        emergency_request.refresh_from_db()
        self.assertEqual(emergency_request.status, 'fulfilled')
        self.assertEqual(emergency_request.fulfilled_by, self.facility)

    def test_requester_is_notified_by_each_confirming_facility(self):
        """If several facilities separately confirm availability, the requester
        should get a notification from each of them, not just the first."""
        second_admin = User.objects.create_user(
            username='hospitaladmin2', password='pass1234', user_type='hospital'
        )
        second_facility = Facility.objects.create(
            admin=second_admin, name='Ikeja General Hospital', facility_type='hospital',
            address='9 General St', state='Lagos', lga='Ikeja', phone='08033333333',
            is_verified=True, is_active=True,
        )
        BloodStock.objects.create(facility=second_facility, blood_type='O+', units_available=3)

        emergency_request = EmergencyRequest.objects.create(
            requester=self.requester, request_type='blood', blood_type='O+', units_needed=1,
            location_text='Ikeja', state='Lagos', lga='Ikeja',
        )
        first_broadcast = BroadcastLog.objects.create(request=emergency_request, facility=self.facility)
        second_broadcast = BroadcastLog.objects.create(request=emergency_request, facility=second_facility)

        self.client.login(username='hospitaladmin', password='pass1234')
        self.client.post(reverse('facility_respond', args=[first_broadcast.id]), {'decision': 'available'})
        self.client.logout()

        self.client.login(username='hospitaladmin2', password='pass1234')
        self.client.post(reverse('facility_respond', args=[second_broadcast.id]), {'decision': 'available'})
        self.client.logout()

        emergency_request.refresh_from_db()
        self.assertEqual(emergency_request.status, 'fulfilled')
        self.assertEqual(emergency_request.fulfilled_by, self.facility)  # first confirmer stays "primary"

        match_notifications = Notification.objects.filter(
            recipient=self.requester, emergency_request=emergency_request, notif_type='match_found',
        )
        notified_facilities = set(match_notifications.values_list('facility_id', flat=True))
        self.assertEqual(notified_facilities, {self.facility.id, second_facility.id})

        self.client.login(username='patient', password='pass1234')
        response = self.client.get(reverse('request_status', args=[emergency_request.pk]))
        self.assertEqual(list(response.context['matched_facilities']), [second_facility, self.facility])

    def test_supply_request_only_broadcasts_to_facility_stocking_that_supply(self):
        """A medication/equipment request should only notify facilities that actually
        stock the requested item — not any facility with some unrelated supply available."""
        stocked_admin = User.objects.create_user(
            username='stockedadmin', password='pass1234', user_type='hospital'
        )
        stocked_facility = Facility.objects.create(
            admin=stocked_admin, name='Ikeja Pharmacy', facility_type='pharmacy',
            address='3 Pharm Rd', state='Lagos', lga='Ikeja', phone='08044444444',
            is_verified=True, is_active=True,
        )
        MedicalSupply.objects.create(
            facility=stocked_facility, supply_name='Paracetamol', category='medication',
            quantity=20, is_available=True,
        )
        # This facility has an unrelated supply available — it should NOT be matched.
        MedicalSupply.objects.create(
            facility=self.facility, supply_name='Oxygen Cylinder', category='oxygen',
            quantity=5, is_available=True,
        )

        self.client.login(username='patient', password='pass1234')
        response = self.client.post(reverse('request_create'), {
            'request_type': 'medication',
            'blood_type': '',
            'units_needed': 1,
            'supply_name': 'Paracetamol',
            'description': '',
            'location_text': 'Ikeja',
            'state': 'Lagos',
            'lga': 'Ikeja',
            'urgency': 'urgent',
        })
        self.assertEqual(response.status_code, 302)

        emergency_request = EmergencyRequest.objects.get()
        self.assertTrue(
            BroadcastLog.objects.filter(request=emergency_request, facility=stocked_facility).exists()
        )
        self.assertFalse(
            BroadcastLog.objects.filter(request=emergency_request, facility=self.facility).exists()
        )

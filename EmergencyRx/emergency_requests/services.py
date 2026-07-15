from django.db import transaction
from django.utils import timezone

from facilities.models import Facility
from inventory.models import BloodStock
from notifications.services import (
    notify_facility_of_request,
    notify_requester_of_broadcast,
    notify_requester_of_match,
)

from .models import BroadcastLog, EmergencyRequest

EXPIRY_HOURS = {
    'critical': 1,
    'urgent': 4,
    'normal': 24,
}


def find_matching_facilities(emergency_request: EmergencyRequest):
    """Facilities in the same state/LGA that could plausibly fulfil this request."""
    queryset = Facility.objects.filter(
        is_verified=True, is_active=True, state__iexact=emergency_request.state,
    )
    if emergency_request.request_type == 'blood':
        queryset = queryset.filter(
            blood_stocks__blood_type=emergency_request.blood_type,
            blood_stocks__units_available__gt=0,
        )
    else:
        queryset = queryset.filter(
            medical_supplies__category=emergency_request.request_type,
            medical_supplies__supply_name__iexact=emergency_request.supply_name,
            medical_supplies__is_available=True,
            medical_supplies__quantity__gt=0,
        )
    same_lga = queryset.filter(lga__iexact=emergency_request.lga)
    matched = same_lga if same_lga.exists() else queryset
    return matched.distinct().order_by('-visibility_points')


@transaction.atomic
def broadcast_request(emergency_request: EmergencyRequest):
    """Create broadcast records for every matching facility and notify them."""
    facilities = find_matching_facilities(emergency_request)
    for facility in facilities:
        broadcast, created = BroadcastLog.objects.get_or_create(
            request=emergency_request, facility=facility,
        )
        if created:
            notify_facility_of_request(facility, emergency_request)
            notify_requester_of_broadcast(emergency_request, facility)

    emergency_request.status = 'broadcasting' if facilities else 'pending'
    hours = EXPIRY_HOURS.get(emergency_request.urgency, 4)
    emergency_request.expires_at = timezone.now() + timezone.timedelta(hours=hours)
    emergency_request.save(update_fields=['status', 'expires_at'])
    return facilities.count()


@transaction.atomic
def respond_to_broadcast(broadcast: BroadcastLog, available: bool, notes: str = ''):
    broadcast.response = 'available' if available else 'unavailable'
    broadcast.responded_at = timezone.now()
    broadcast.notes = notes
    broadcast.save(update_fields=['response', 'responded_at', 'notes'])

    if available:
        request = broadcast.request
        if request.status != 'fulfilled':
            request.status = 'fulfilled'
            request.fulfilled_by = broadcast.facility
            request.fulfilled_at = timezone.now()
            request.save(update_fields=['status', 'fulfilled_by', 'fulfilled_at'])
        # Notify the requester for every facility that confirms availability,
        # not just the first — several facilities may separately have the supply/blood.
        notify_requester_of_match(request, broadcast.facility)
    return broadcast

from django.conf import settings

from .backends.console import ConsoleSMSBackend
from .backends.termii import TermiiSMSBackend
from .backends.twilio import TwilioSMSBackend
from .models import Notification

BACKENDS = {
    'console': ConsoleSMSBackend,
    'termii': TermiiSMSBackend,
    'twilio': TwilioSMSBackend,
}


def get_backend():
    name = getattr(settings, 'SMS_BACKEND', 'console')
    return BACKENDS.get(name, ConsoleSMSBackend)()


def send_sms(to: str, message: str) -> bool:
    return get_backend().send(to, message)


def notify_facility_of_request(facility, emergency_request):
    label = emergency_request.blood_type or emergency_request.supply_name or emergency_request.request_type
    message = (
        f"EmergencyRx ALERT: {emergency_request.units_needed} unit(s) of {label} needed "
        f"in {emergency_request.lga}, {emergency_request.state}. "
        f"Urgency: {emergency_request.get_urgency_display()}. "
        f"Log in to your dashboard to respond."
    )
    return send_sms(facility.phone, message)


def notify_requester_of_broadcast(emergency_request, facility):
    """Let the requester know a facility has received their request, with its location."""
    message = (
        f"{facility.name} ({facility.lga}, {facility.state}) has received your request "
        f"and may have what you need. We'll notify you again once they confirm availability."
    )
    Notification.objects.create(
        recipient=emergency_request.requester,
        notif_type='broadcast_sent',
        emergency_request=emergency_request,
        facility=facility,
        message=message,
    )


def notify_requester_of_match(emergency_request, facility):
    message = (
        f"MATCHED! {facility.name} has confirmed availability. "
        f"Address: {facility.address}. Call: {facility.phone}"
    )
    Notification.objects.create(
        recipient=emergency_request.requester,
        notif_type='match_found',
        emergency_request=emergency_request,
        facility=facility,
        message=message,
    )
    return send_sms(emergency_request.requester.phone_number, message)

import json
import logging
import urllib.request

from django.conf import settings

from .base import BaseSMSBackend

logger = logging.getLogger('notifications')

TERMII_URL = 'https://api.ng.termii.com/api/sms/send'


class TermiiSMSBackend(BaseSMSBackend):
    """Sends SMS via Termii — the recommended provider for Nigerian numbers."""

    def send(self, to: str, message: str) -> bool:
        api_key = getattr(settings, 'TERMII_API_KEY', '')
        sender_id = getattr(settings, 'TERMII_SENDER_ID', 'EmergencyRx')
        if not api_key:
            logger.warning("TERMII_API_KEY not configured — skipping SMS to %s", to)
            return False

        payload = json.dumps({
            'to': to,
            'from': sender_id,
            'sms': message,
            'type': 'plain',
            'channel': 'generic',
            'api_key': api_key,
        }).encode('utf-8')
        request = urllib.request.Request(
            TERMII_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST'
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status == 200
        except Exception:
            logger.exception("Termii SMS delivery failed for %s", to)
            return False

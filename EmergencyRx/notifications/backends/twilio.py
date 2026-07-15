import base64
import logging
import urllib.parse
import urllib.request

from django.conf import settings

from .base import BaseSMSBackend

logger = logging.getLogger('notifications')


class TwilioSMSBackend(BaseSMSBackend):
    """Sends SMS via Twilio — fallback provider for international numbers."""

    def send(self, to: str, message: str) -> bool:
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        if not (account_sid and auth_token and from_number):
            logger.warning("Twilio credentials not configured — skipping SMS to %s", to)
            return False

        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        payload = urllib.parse.urlencode({'To': to, 'From': from_number, 'Body': message}).encode()
        credentials = base64.b64encode(f'{account_sid}:{auth_token}'.encode()).decode()
        request = urllib.request.Request(
            url, data=payload,
            headers={'Authorization': f'Basic {credentials}'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status in (200, 201)
        except Exception:
            logger.exception("Twilio SMS delivery failed for %s", to)
            return False

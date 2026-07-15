import logging

from .base import BaseSMSBackend

logger = logging.getLogger('notifications')


class ConsoleSMSBackend(BaseSMSBackend):
    """Default backend for local development — logs instead of sending a real SMS."""

    def send(self, to: str, message: str) -> bool:
        logger.info("SMS to %s: %s", to, message)
        return True

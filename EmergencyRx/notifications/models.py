from django.conf import settings
from django.db import models


class Notification(models.Model):
    NOTIF_TYPES = (
        ('match_found', 'Matching Facility Found'),
        ('broadcast_sent', 'Request Broadcast'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES, default='match_found')
    emergency_request = models.ForeignKey(
        'emergency_requests.EmergencyRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
    )
    facility = models.ForeignKey(
        'facilities.Facility', on_delete=models.SET_NULL, null=True, blank=True
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:40]}"

from django.conf import settings
from django.db import models

from facilities.models import Facility
from inventory.models import BloodStock


class EmergencyRequest(models.Model):
    REQUEST_TYPES = (
        ('blood', 'Blood'),
        ('oxygen', 'Oxygen'),
        ('medication', 'Medication'),
        ('equipment', 'Medical Equipment'),
    )
    URGENCY_LEVELS = (
        ('critical', 'Critical — Life Threatening'),
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
    )
    STATUSES = (
        ('pending', 'Pending'),
        ('broadcasting', 'Broadcasting to Facilities'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_requests'
    )
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    blood_type = models.CharField(
        max_length=3,
        choices=BloodStock.BLOOD_TYPES,
        blank=True,
        null=True,
        help_text='Required if request type is blood',
    )
    units_needed = models.PositiveIntegerField(default=1)
    supply_name = models.CharField(
        max_length=255, blank=True, help_text='Required for medication or equipment requests'
    )
    description = models.TextField(blank=True)
    location_text = models.CharField(max_length=255, help_text='Describe your location (e.g. Surulere, Lagos)')
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100, verbose_name='Local Government Area')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS, default='urgent')
    status = models.CharField(max_length=15, choices=STATUSES, default='pending')
    fulfilled_by = models.ForeignKey(
        Facility,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fulfilled_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        label = self.blood_type if self.request_type == 'blood' else self.supply_name
        return f"Request #{self.pk} — {self.request_type} ({label}) by {self.requester.username}"


class BroadcastLog(models.Model):
    RESPONSE_CHOICES = (
        ('pending', 'Awaiting Response'),
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
    )

    request = models.ForeignKey(
        EmergencyRequest, on_delete=models.CASCADE, related_name='broadcasts'
    )
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name='received_broadcasts'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    response = models.CharField(max_length=15, choices=RESPONSE_CHOICES, default='pending')
    responded_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('request', 'facility')
        ordering = ['-sent_at']

    def __str__(self):
        return f"Broadcast → {self.facility.name} for Request #{self.request.pk} [{self.response}]"

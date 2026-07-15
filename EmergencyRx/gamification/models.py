from django.conf import settings
from django.db import models

from facilities.models import Facility


class StockUpdateLog(models.Model):
    STOCK_TYPES = (
        ('blood', 'Blood'),
        ('supply', 'Medical Supply'),
    )

    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name='stock_update_logs'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_log_entries'
    )
    stock_type = models.CharField(max_length=10, choices=STOCK_TYPES)
    blood_type = models.CharField(max_length=3, blank=True, null=True)
    supply_name = models.CharField(max_length=255, blank=True)
    points_awarded = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        label = self.blood_type or self.supply_name
        return f"{self.facility.name} updated {label} (+{self.points_awarded} pts)"

from django.conf import settings
from django.db import models

from facilities.models import Facility


class BloodStock(models.Model):
    BLOOD_TYPES = (
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
    )

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='blood_stocks')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    units_available = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blood_stock_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('facility', 'blood_type')
        ordering = ['blood_type']

    def __str__(self):
        return f"{self.facility.name} — {self.blood_type}: {self.units_available} units"

    @property
    def is_available(self):
        return self.units_available > 0


class MedicalSupply(models.Model):
    CATEGORIES = (
        ('oxygen', 'Oxygen'),
        ('medication', 'Medication'),
        ('equipment', 'Medical Equipment'),
        ('blood_product', 'Blood Product'),
    )

    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name='medical_supplies'
    )
    supply_name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    quantity = models.PositiveIntegerField(default=0)
    unit_of_measure = models.CharField(max_length=50, default='units')
    expiry_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='supply_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Medical Supplies'
        ordering = ['category', 'supply_name']

    def __str__(self):
        return f"{self.facility.name} — {self.supply_name} ({self.quantity} {self.unit_of_measure})"

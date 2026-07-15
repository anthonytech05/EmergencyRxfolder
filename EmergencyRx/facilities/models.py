from django.conf import settings
from django.db import models
from django.utils import timezone


class Facility(models.Model):
    FACILITY_TYPES = (
        ('hospital', 'Hospital'),
        ('blood_bank', 'Blood Bank'),
        ('clinic', 'Clinic'),
        ('pharmacy', 'Pharmacy'),
    )
    SUBSCRIPTION_STATUS = (
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_facilities'
    )
    name = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='hospital')
    address = models.TextField()
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100, verbose_name='Local Government Area')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_STATUS, default='inactive'
    )
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    visibility_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Facilities'
        ordering = ['-visibility_points', 'name']
        indexes = [
            models.Index(fields=['state', 'lga']),
            models.Index(fields=['facility_type', 'is_verified']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"

    @property
    def subscription_is_active(self):
        return (
            self.subscription_status == 'active'
            and self.subscription_expires_at
            and self.subscription_expires_at > timezone.now()
        )


class Subscription(models.Model):
    PLANS = (
        ('basic', 'Basic — ₦10,000/month'),
        ('premium', 'Premium — ₦25,000/month'),
    )
    PAYMENT_STATUSES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name='subscriptions'
    )
    plan = models.CharField(max_length=10, choices=PLANS, default='basic')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUSES, default='pending')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.facility.name} — {self.get_plan_display()} [{self.payment_status}]"

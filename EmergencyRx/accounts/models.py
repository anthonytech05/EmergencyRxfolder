import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('hospital', 'Hospital Staff'),
        ('public', 'Public User'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='public')
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class EmergencyCard(models.Model):
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
    GENOTYPES = (
        ('AA', 'AA'),
        ('AS', 'AS'),
        ('SS', 'SS'),
        ('AC', 'AC'),
        ('SC', 'SC'),
    )

    card_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emergency_card')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    genotype = models.CharField(max_length=2, choices=GENOTYPES, blank=True)
    allergies = models.TextField(blank=True, help_text='List known allergies, comma-separated')
    medical_conditions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"EmergencyCard — {self.owner.get_full_name() or self.owner.username} ({self.blood_type})"

    @property
    def qr_data(self):
        return str(self.card_uid)


class EmergencyContact(models.Model):
    card = models.ForeignKey(
        EmergencyCard, on_delete=models.CASCADE, related_name='emergency_contacts'
    )
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} ({self.relationship}) — {self.phone_number}"

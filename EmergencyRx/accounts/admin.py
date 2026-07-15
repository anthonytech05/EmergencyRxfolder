from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmergencyCard, EmergencyContact, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('EmergencyRx', {'fields': ('user_type', 'phone_number')}),
    )
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 1
    fields = ('name', 'relationship', 'phone_number', 'is_primary')


@admin.register(EmergencyCard)
class EmergencyCardAdmin(admin.ModelAdmin):
    inlines = [EmergencyContactInline]
    list_display = ('owner', 'blood_type', 'genotype', 'is_active', 'issued_at')
    list_filter = ('blood_type', 'genotype', 'is_active')
    search_fields = ('owner__username', 'owner__email', 'card_uid')
    readonly_fields = ('card_uid', 'issued_at', 'qr_data')
    fieldsets = (
        ('Card Info', {
            'fields': ('card_uid', 'qr_data', 'owner', 'is_active', 'payment_reference'),
        }),
        ('Medical Profile', {
            'fields': ('blood_type', 'genotype', 'allergies', 'medical_conditions'),
        }),
        ('Timestamps', {
            'fields': ('issued_at',),
            'classes': ('collapse',),
        }),
    )


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'relationship', 'phone_number', 'is_primary', 'card')
    list_filter = ('relationship', 'is_primary')
    search_fields = ('name', 'phone_number', 'card__owner__username')

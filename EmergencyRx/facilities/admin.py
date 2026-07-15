from django.contrib import admin

from inventory.models import BloodStock, MedicalSupply

from .models import Facility, Subscription


class BloodStockInline(admin.TabularInline):
    model = BloodStock
    extra = 0
    fields = ('blood_type', 'units_available', 'expiry_date', 'last_updated_by')
    readonly_fields = ('updated_at',)


class MedicalSupplyInline(admin.TabularInline):
    model = MedicalSupply
    extra = 0
    fields = ('supply_name', 'category', 'quantity', 'unit_of_measure', 'is_available')


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    inlines = [BloodStockInline, MedicalSupplyInline]
    list_display = (
        'name', 'facility_type', 'state', 'lga',
        'subscription_status', 'visibility_points', 'is_verified', 'is_active',
    )
    list_filter = ('facility_type', 'state', 'subscription_status', 'is_verified', 'is_active')
    search_fields = ('name', 'address', 'state', 'lga', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'visibility_points')
    list_editable = ('is_verified', 'is_active')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'facility_type', 'admin', 'phone', 'email', 'website'),
        }),
        ('Location', {
            'fields': ('address', 'state', 'lga', 'latitude', 'longitude'),
        }),
        ('Status & Subscription', {
            'fields': (
                'is_verified', 'is_active',
                'subscription_status', 'subscription_expires_at',
                'visibility_points',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('facility', 'plan', 'amount', 'payment_status', 'start_date', 'end_date', 'created_at')
    list_filter = ('plan', 'payment_status')
    search_fields = ('facility__name', 'payment_reference')
    readonly_fields = ('created_at',)

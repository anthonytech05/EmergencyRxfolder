from django.contrib import admin

from .models import BloodStock, MedicalSupply


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ('facility', 'blood_type', 'units_available', 'expiry_date', 'updated_at')
    list_filter = ('blood_type', 'facility__state')
    search_fields = ('facility__name',)
    readonly_fields = ('updated_at',)


@admin.register(MedicalSupply)
class MedicalSupplyAdmin(admin.ModelAdmin):
    list_display = (
        'facility', 'supply_name', 'category', 'quantity', 'unit_of_measure', 'is_available', 'updated_at'
    )
    list_filter = ('category', 'is_available', 'facility__state')
    search_fields = ('supply_name', 'facility__name')
    readonly_fields = ('updated_at',)

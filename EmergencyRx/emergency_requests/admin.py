from django.contrib import admin

from .models import BroadcastLog, EmergencyRequest


class BroadcastLogInline(admin.TabularInline):
    model = BroadcastLog
    extra = 0
    fields = ('facility', 'response', 'sent_at', 'responded_at', 'notes')
    readonly_fields = ('sent_at',)


@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    inlines = [BroadcastLogInline]
    list_display = (
        'id', 'requester', 'request_type', 'blood_type', 'units_needed',
        'urgency', 'status', 'state', 'lga', 'created_at',
    )
    list_filter = ('request_type', 'urgency', 'status', 'state')
    search_fields = ('requester__username', 'location_text', 'supply_name')
    readonly_fields = ('created_at', 'fulfilled_at')
    fieldsets = (
        ('Request Details', {
            'fields': (
                'requester', 'request_type', 'blood_type', 'units_needed',
                'supply_name', 'description', 'urgency',
            ),
        }),
        ('Location', {
            'fields': ('location_text', 'state', 'lga', 'latitude', 'longitude'),
        }),
        ('Status', {
            'fields': ('status', 'fulfilled_by'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'fulfilled_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(BroadcastLog)
class BroadcastLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'facility', 'response', 'sent_at', 'responded_at')
    list_filter = ('response',)
    search_fields = ('facility__name', 'request__id')
    readonly_fields = ('sent_at',)

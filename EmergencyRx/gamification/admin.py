from django.contrib import admin

from .models import StockUpdateLog


@admin.register(StockUpdateLog)
class StockUpdateLogAdmin(admin.ModelAdmin):
    list_display = ('facility', 'updated_by', 'stock_type', 'blood_type', 'supply_name', 'points_awarded', 'created_at')
    list_filter = ('stock_type', 'facility__state')
    search_fields = ('facility__name', 'updated_by__username')
    readonly_fields = ('created_at',)

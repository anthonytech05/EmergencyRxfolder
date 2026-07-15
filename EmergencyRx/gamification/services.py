from django.db import transaction

from facilities.models import Facility

from .models import StockUpdateLog

DAILY_STOCK_UPDATE_POINTS = 10
FAST_RESPONSE_POINTS = 25
SUCCESSFUL_MATCH_POINTS = 50
VERIFICATION_POINTS = 100


def award_points(facility: Facility, points: int, stock_type: str, updated_by=None,
                  blood_type: str = '', supply_name: str = ''):
    """Log a points transaction and update the facility's running total."""
    with transaction.atomic():
        StockUpdateLog.objects.create(
            facility=facility,
            updated_by=updated_by,
            stock_type=stock_type,
            blood_type=blood_type,
            supply_name=supply_name,
            points_awarded=points,
        )
        facility.visibility_points += points
        facility.save(update_fields=['visibility_points'])


def get_leaderboard(state: str = None, limit: int = 20):
    queryset = Facility.objects.filter(is_verified=True, is_active=True)
    if state:
        queryset = queryset.filter(state__iexact=state)
    return queryset.order_by('-visibility_points', 'name')[:limit]

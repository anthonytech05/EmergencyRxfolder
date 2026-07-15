def pending_broadcasts(request):
    if not request.user.is_authenticated or request.user.user_type != 'hospital':
        return {'facility_pending_count': 0}
    facility = request.user.managed_facilities.first()
    if facility is None:
        return {'facility_pending_count': 0}
    count = facility.received_broadcasts.filter(response='pending').count()
    return {'facility_pending_count': count}

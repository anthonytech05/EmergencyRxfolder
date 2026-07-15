from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def facility_required(view_func):
    """Ensure the logged-in user is hospital staff who owns a registered facility."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        facility = request.user.managed_facilities.first()
        if facility is None:
            messages.info(request, 'Register your facility first to access this page.')
            return redirect('facility_register')
        return view_func(request, facility, *args, **kwargs)

    return wrapper

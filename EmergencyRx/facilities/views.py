from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from emergency_requests.models import BroadcastLog
from emergency_requests.services import respond_to_broadcast
from gamification.services import get_leaderboard
from inventory.models import BloodStock

from .decorators import facility_required
from .forms import FacilityForm
from .models import Facility
from .nigeria_data import NIGERIA_STATES, NIGERIA_STATES_LGAS

BLOOD_TYPES = BloodStock.BLOOD_TYPES


@login_required
def facility_register(request):
    existing = request.user.managed_facilities.first()
    if existing:
        return redirect('facility_dashboard')

    if request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            facility = form.save(commit=False)
            facility.admin = request.user
            facility.save()
            request.user.user_type = 'hospital'
            request.user.save(update_fields=['user_type'])
            messages.success(
                request,
                'Facility submitted for verification! Our team reviews new facilities within 24-48 hours.'
            )
            return redirect('facility_dashboard')
    else:
        form = FacilityForm()
    return render(request, 'facility/register.html', {'form': form})


@facility_required
def facility_dashboard(request, facility):
    broadcasts = facility.received_broadcasts.select_related('request').order_by('-sent_at')[:10]
    total_broadcasts = facility.received_broadcasts.count()
    responded = facility.received_broadcasts.exclude(response='pending').count()
    response_rate = round((responded / total_broadcasts) * 100, 1) if total_broadcasts else 0.0

    context = {
        'facility': facility,
        'blood_stocks': facility.blood_stocks.all(),
        'medical_supplies': facility.medical_supplies.all(),
        'broadcasts': broadcasts,
        'response_rate': response_rate,
        'pending_count': facility.received_broadcasts.filter(response='pending').count(),
    }
    return render(request, 'facility/dashboard.html', context)


@facility_required
def facility_profile(request, facility):
    if request.method == 'POST':
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facility profile updated.')
            return redirect('facility_profile')
    else:
        form = FacilityForm(instance=facility)
    return render(request, 'facility/profile.html', {'form': form, 'facility': facility})


@facility_required
def facility_requests_list(request, facility):
    broadcasts = facility.received_broadcasts.select_related('request', 'request__requester').order_by('-sent_at')
    return render(request, 'facility/requests.html', {'facility': facility, 'broadcasts': broadcasts})


@facility_required
def facility_respond(request, facility, broadcast_id):
    broadcast = get_object_or_404(BroadcastLog, id=broadcast_id, facility=facility)
    if request.method == 'POST':
        available = request.POST.get('decision') == 'available'
        notes = request.POST.get('notes', '')
        respond_to_broadcast(broadcast, available, notes)
        messages.success(
            request,
            'Marked as available — the requester has been notified.' if available
            else 'Marked as unavailable.'
        )
    return redirect('facility_requests')


@login_required
def facility_search(request):
    state = request.GET.get('state', '').strip()
    lga = request.GET.get('lga', '').strip()
    blood_type = request.GET.get('blood_type', '').strip()
    facility_type = request.GET.get('facility_type', '').strip()

    results = Facility.objects.filter(is_verified=True, is_active=True)
    if state:
        results = results.filter(state__iexact=state)
    if lga:
        results = results.filter(lga__iexact=lga)
    if facility_type:
        results = results.filter(facility_type=facility_type)
    if blood_type:
        results = results.filter(blood_stocks__blood_type=blood_type, blood_stocks__units_available__gt=0)
    results = results.distinct().order_by('-visibility_points', 'name')

    context = {
        'results': results,
        'state': state,
        'lga': lga,
        'blood_type': blood_type,
        'facility_type': facility_type,
        'blood_type_choices': BLOOD_TYPES,
        'facility_type_choices': Facility.FACILITY_TYPES,
        'states': NIGERIA_STATES,
        'states_lgas': NIGERIA_STATES_LGAS,
        'searched': bool(state or lga or blood_type or facility_type),
    }
    return render(request, 'search/results.html', context)


def leaderboard(request):
    state = request.GET.get('state') or None
    lga = request.GET.get('lga') or None
    facilities = get_leaderboard(state=state, lga=lga)
    return render(request, 'leaderboard.html', {
        'facilities': facilities,
        'selected_state': state,
        'selected_lga': lga,
        'states': NIGERIA_STATES,
        'states_lgas': NIGERIA_STATES_LGAS,
    })

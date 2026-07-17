from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from facilities.nigeria_data import NIGERIA_STATES_LGAS

from .forms import EmergencyRequestForm
from .models import EmergencyRequest
from .services import broadcast_request


@login_required
def request_create(request):
    if request.method == 'POST':
        form = EmergencyRequestForm(request.POST)
        if form.is_valid():
            emergency_request = form.save(commit=False)
            emergency_request.requester = request.user
            emergency_request.status = 'pending'
            emergency_request.save()

            matched_count = broadcast_request(emergency_request)
            if matched_count:
                messages.success(
                    request,
                    f'Request broadcast to {matched_count} nearby facilit{"y" if matched_count == 1 else "ies"}. '
                    "You'll be notified as soon as one confirms."
                )
            else:
                messages.warning(
                    request,
                    'No verified facility currently matches your request in your area. '
                    'We will keep watching and notify you if one becomes available.'
                )
            return redirect('request_status', pk=emergency_request.pk)
    else:
        form = EmergencyRequestForm()
    return render(request, 'request/create.html', {'form': form, 'states_lgas': NIGERIA_STATES_LGAS})


@login_required
def request_status(request, pk):
    emergency_request = get_object_or_404(EmergencyRequest, pk=pk, requester=request.user)
    broadcasts = emergency_request.broadcasts.select_related('facility').order_by('-sent_at')
    matched_facilities = [b.facility for b in broadcasts if b.response == 'available']
    return render(request, 'request/status.html', {
        'emergency_request': emergency_request,
        'broadcasts': broadcasts,
        'matched_facilities': matched_facilities,
    })


@login_required
def my_requests(request):
    requests_qs = EmergencyRequest.objects.filter(requester=request.user).order_by('-created_at')
    return render(request, 'request/my_requests.html', {'requests': requests_qs})

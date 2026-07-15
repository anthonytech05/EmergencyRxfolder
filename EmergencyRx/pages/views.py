from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from emergency_requests.models import EmergencyRequest
from facilities.models import Facility
from inventory.models import BloodStock

from .forms import TestimonialForm
from .models import Testimonial


def _build_live_ticker(limit=6):
    items = []

    live_requests = EmergencyRequest.objects.filter(
        status__in=('pending', 'broadcasting')
    ).select_related().order_by('-created_at')[:limit]
    for req in live_requests:
        label = req.blood_type or req.supply_name or req.get_request_type_display()
        items.append({
            'kind': 'live',
            'label': 'LIVE',
            'text': f'{req.units_needed} unit(s) of {label} needed — {req.lga}, {req.state}',
            'created_at': req.created_at,
        })

    fulfilled = EmergencyRequest.objects.filter(status='fulfilled').select_related(
        'fulfilled_by'
    ).order_by('-fulfilled_at')[:limit]
    for req in fulfilled:
        facility_name = req.fulfilled_by.name if req.fulfilled_by else 'a partner facility'
        items.append({
            'kind': 'fulfilled',
            'label': 'FULFILLED',
            'text': f'Blood/supply request matched at {facility_name}',
            'created_at': req.fulfilled_at,
        })

    new_facilities = Facility.objects.filter(is_verified=True).order_by('-created_at')[:limit]
    for facility in new_facilities:
        items.append({
            'kind': 'new',
            'label': 'NEW',
            'text': f'{facility.name} joined EmergencyRx',
            'created_at': facility.created_at,
        })

    epoch = timezone.make_aware(timezone.datetime.min.replace(year=1970))
    items.sort(key=lambda item: item['created_at'] or epoch, reverse=True)
    return items[:limit]


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin:index')

    context = {
        'facility_count': Facility.objects.filter(is_active=True, is_verified=True).count(),
        'request_count': EmergencyRequest.objects.count(),
        'fulfilled_count': EmergencyRequest.objects.filter(status='fulfilled').count(),
        'state_count': Facility.objects.values('state').distinct().count(),
        'blood_available': BloodStock.objects.filter(units_available__gt=0).values('blood_type').distinct().count(),
        'recent_facilities': Facility.objects.filter(
            is_active=True, is_verified=True
        ).order_by('-visibility_points')[:6],
        'live_ticker': _build_live_ticker(),
        'testimonials': Testimonial.objects.filter(is_approved=True).select_related('user')[:6],
    }
    return render(request, 'home.html', context)


def about(request):
    return render(request, 'pages/about.html')


@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            messages.success(
                request,
                "Thank you for sharing your story! It'll appear on our homepage once reviewed."
            )
            return redirect('home')
    else:
        form = TestimonialForm()
    return render(request, 'pages/submit_testimonial.html', {'form': form})

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from facilities.decorators import facility_required
from gamification.services import DAILY_STOCK_UPDATE_POINTS, award_points

from .forms import BloodStockForm, MedicalSupplyForm
from .models import BloodStock, MedicalSupply


@facility_required
def inventory_home(request, facility):
    return render(request, 'facility/inventory.html', {
        'facility': facility,
        'blood_stocks': facility.blood_stocks.all(),
        'medical_supplies': facility.medical_supplies.all(),
        'blood_form': BloodStockForm(),
        'supply_form': MedicalSupplyForm(),
    })


@facility_required
def blood_stock_save(request, facility):
    stock_id = request.POST.get('stock_id')
    instance = get_object_or_404(BloodStock, id=stock_id, facility=facility) if stock_id else None
    form = BloodStockForm(request.POST, instance=instance)
    if form.is_valid():
        stock = form.save(commit=False)
        stock.facility = facility
        stock.last_updated_by = request.user
        stock.save()
        award_points(facility, DAILY_STOCK_UPDATE_POINTS, 'blood', request.user, blood_type=stock.blood_type)
        messages.success(request, f'{stock.get_blood_type_display()} stock updated (+{DAILY_STOCK_UPDATE_POINTS} points).')
    else:
        messages.error(request, 'Could not save blood stock — check the form and try again.')
    return redirect('inventory_home')


@facility_required
def medical_supply_save(request, facility):
    supply_id = request.POST.get('supply_id')
    instance = get_object_or_404(MedicalSupply, id=supply_id, facility=facility) if supply_id else None
    form = MedicalSupplyForm(request.POST, instance=instance)
    if form.is_valid():
        supply = form.save(commit=False)
        supply.facility = facility
        supply.last_updated_by = request.user
        supply.save()
        award_points(facility, DAILY_STOCK_UPDATE_POINTS, 'supply', request.user, supply_name=supply.supply_name)
        messages.success(request, f'{supply.supply_name} updated (+{DAILY_STOCK_UPDATE_POINTS} points).')
    else:
        messages.error(request, 'Could not save supply — check the form and try again.')
    return redirect('inventory_home')


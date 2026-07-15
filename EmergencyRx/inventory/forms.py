from django import forms

from .models import BloodStock, MedicalSupply


class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ('blood_type', 'units_available', 'expiry_date')
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MedicalSupplyForm(forms.ModelForm):
    class Meta:
        model = MedicalSupply
        fields = ('supply_name', 'category', 'quantity', 'unit_of_measure', 'expiry_date', 'is_available')
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

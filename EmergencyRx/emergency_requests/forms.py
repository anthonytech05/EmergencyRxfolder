from django import forms

from facilities.nigeria_data import NIGERIA_STATES

from .models import EmergencyRequest


class EmergencyRequestForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[(s, s) for s in NIGERIA_STATES])

    class Meta:
        model = EmergencyRequest
        fields = (
            'request_type', 'blood_type', 'units_needed', 'supply_name', 'description',
            'location_text', 'state', 'lga', 'urgency',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('request_type')
        if request_type == 'blood' and not cleaned_data.get('blood_type'):
            self.add_error('blood_type', 'Select a blood type for a blood request.')
        if request_type != 'blood' and not cleaned_data.get('supply_name'):
            self.add_error('supply_name', 'Describe the supply or medication you need.')
        return cleaned_data

from django import forms

from .models import Facility
from .nigeria_data import NIGERIA_STATES


class FacilityForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[(s, s) for s in NIGERIA_STATES])

    class Meta:
        model = Facility
        fields = (
            'name', 'facility_type', 'address', 'state', 'lga',
            'phone', 'email', 'website',
        )
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

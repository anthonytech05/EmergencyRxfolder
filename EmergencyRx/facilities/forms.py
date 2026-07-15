from django import forms

from .models import Facility

NIGERIA_STATES = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
    'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo',
    'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
    'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba',
    'Yobe', 'Zamfara',
]


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

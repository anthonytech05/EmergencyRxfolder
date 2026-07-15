from django import forms

from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ('quote', 'rating', 'location')
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us how EmergencyRx helped you...'}),
        }

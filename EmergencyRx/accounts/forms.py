from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First name', 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last name', 'autocomplete': 'family-name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'autocomplete': 'email'})
    )
    phone_number = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': '+234 800 000 0000', 'autocomplete': 'tel'})
    )
    user_type = forms.ChoiceField(
        choices=[
            ('', '— Select account type —'),
            ('public', 'Public User — I need medical supplies'),
            ('hospital', 'Hospital / Blood Bank Staff'),
        ],
        required=True
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email',
            'phone_number', 'user_type', 'password1', 'password2'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username', 'autocomplete': 'username'
            }),
        }

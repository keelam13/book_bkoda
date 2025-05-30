from django import forms
from datetime import date

class TripSearchForm(forms.Form):
    origin = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'From', 'class': 'form-control'}),
        label=""
    )
    destination = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'To', 'class': 'form-control'}),
        label=""
    )
    departure_date = forms.DateField(
        required=False,
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label=""
    )
    num_travelers = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'placeholder': '1 Passenger', 'min': '1', 'class': 'form-control'}),
        label=""
    )
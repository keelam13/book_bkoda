from django import forms
from datetime import date


class TripSearchForm(forms.Form):
    origin = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'From', 'class': 'form-control'}),
        label=""
    )
    destination = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'To', 'class': 'form-control'}),
        label=""
    )
    departure_date = forms.DateField(
        required=False,
        initial=date.today,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}),
        label=""
    )
    num_travelers = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=12,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '1 Passenger',
                'min': '1',
                'max': '12',
                'class': 'form-control'}),
        label=""
    )

    def __init__(self, *args, **kwargs):
        is_rescheduling_mode = kwargs.pop('is_rescheduling_mode', False)
        fixed_num_travelers = kwargs.pop('fixed_num_travelers', None)
        super().__init__(*args, **kwargs)

        if is_rescheduling_mode:
            if fixed_num_travelers is not None:
                self.fields['num_travelers'].initial = fixed_num_travelers
            self.fields['num_travelers'].widget.attrs['readonly'] = True
            self.fields['num_travelers'].help_text = \
                "Number of travelers is fixed for reschedule."

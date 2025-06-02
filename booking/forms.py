from django import forms
from .models import Booking


class BookingConfirmationForm(forms.ModelForm):
    """
    Form for confirming a booking and potentially collecting passenger details.

    This form is designed to be used on the booking confirmation page.
    It doesn't directly ask for number_of_passengers as a field,
    as that value is passed to the view from the previous trip search step.
    Instead, it can be extended to collect names for each passenger.
    """

    class Meta:
        model = Booking
        fields = []

    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        self.num_passengers = kwargs.pop('num_passengers', 1)
        super().__init__(*args, **kwargs)

        for i in range(self.num_passengers):
            self.fields[f'passenger_name_{i+1}'] = forms.CharField(
                label=f'Passenger {i+1} Name',
                max_length=100,
                required=True,
                widget=forms.TextInput(attrs={'placeholder': f'Full Name of Passenger {i+1}'})
            )

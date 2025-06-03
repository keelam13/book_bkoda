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
                    label=f'Passenger {i+1}',
                    max_length=100,
                    required=True,
                    widget=forms.TextInput(attrs={'placeholder': f'Full Name {i+1}'})
            )

            self.fields[f'passenger_age_{i+1}'] = forms.IntegerField(
                    label='Age',
                    min_value=0,
                    required=True,
                    widget=forms.NumberInput(attrs={'placeholder': f'Age of Passenger {i+1}', 'class': 'form-control'})
            )

            self.fields[f'passenger_email_{i+1}'] = forms.CharField(
                    label='Email Address',
                    max_length=255,
                    required=True,
                    widget=forms.TextInput(attrs={'placeholder': f'Email Address of Passenger {i+1}', 'class': 'form-control'})
            )

            self.fields[f'passenger_contact_{i+1}'] = forms.CharField(
                    label='Contact Number',
                    max_length=20,
                    required=True,
                    widget=forms.TextInput(attrs={'placeholder': f'Contact Number of Passenger {i+1}', 'class': 'form-control'})
            )
            
    def clean(self):
        cleaned_data = super().clean()

        if self.trip and self.trip.available_seats < self.num_passengers:
            raise forms.ValidationError(
                f"Not enough available seats for {self.num_passengers} passengers. Only {self.trip.available_seats} seats remaining."
            )

        return cleaned_data


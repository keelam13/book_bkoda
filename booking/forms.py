from django import forms
from .models import Booking
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import re


class BookingConfirmationForm(forms.ModelForm):
    """
    Form for confirming a booking and potentially collecting passenger details.

    This form is designed to be used on the booking confirmation page.
    It doesn't directly ask for number_of_passengers as a field,
    as that value is passed to the view from the previous trip search step.
    Instead, it can be extended to collect names for each passenger.
    """

    save_info = forms.BooleanField(
        label='Save this information to my profile for future bookings',
        required=False,
        initial=True
    )

    class Meta:
        model = Booking
        fields = []

    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        self.num_passengers = kwargs.pop('num_passengers', 1)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if not self.request or not self.request.user.is_authenticated:
            if 'save_info' in self.fields:
                del self.fields['save_info']

        for i in range(self.num_passengers):
            passenger_number = i+1

            # Define each passenger field with unique names
            self.fields[f'passenger_name{passenger_number}'] = forms.CharField(
                max_length=100,
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'passenger-details-form',
                    'placeholder':
                        f'Full Name (Passenger {passenger_number}) *'
                })
            )
            self.fields[f'passenger_age{passenger_number}'] =\
            forms.IntegerField(
                min_value=0,
                required=False,
                widget=forms.NumberInput(attrs={
                    'class': 'passenger-details-form',
                    'placeholder': f'Age (Passenger {passenger_number})'
                })
            )
            self.fields[f'passenger_email{passenger_number}'] =\
            forms.EmailField(
                max_length=255,
                required=True,
                widget=forms.EmailInput(attrs={
                    'class': 'passenger-details-form',
                    'placeholder':
                        f'Email Address (Passenger {passenger_number}) *'
                })
            )
            self.fields[f'passenger_contact_number{passenger_number}'] =\
            forms.CharField(
                max_length=20,
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'passenger-details-form',
                    'placeholder':
                        f'Contact Number (Passenger {passenger_number}) *'
                })
            )

        for field_name, field_obj in self.fields.items():
            if field_name.startswith('passenger') or\
            field_name.startswith('save_info'):
                if field_name == 'save_info':
                    field_obj.widget.attrs['class'] = 'form-check-input'
                else:
                    field_obj.widget.attrs['class'] = 'passenger-details-form'
                    field_obj.label = ''

        if 'passenger_name1' in self.fields:
            self.fields['passenger_name1'].widget.attrs['autofocus'] = True

    def clean(self):
        cleaned_data = super().clean()

        if self.trip and self.trip.available_seats < self.num_passengers:
            self.add_error(
                None,
                (f"Not enough available seats for {self.num_passengers}"
                    f"passengers."
                    f"Only {self.trip.available_seats} seats remaining.")
            )

        return cleaned_data


class BillingDetailsForm(forms.Form):
    """
    A form for collecting billing details.
    Card element fields are handled by Stripe.js, not directly here.
    """

    save_info = forms.BooleanField(
        label='Save this information to my profile for future bookings',
        required=False,
        initial=True
    )

    billing_name = forms.CharField(
        label="Name on Card",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder':
                'Full Name (as it appears on card)',
            'autocomplete': 'name'
        })
    )
    billing_email = forms.EmailField(
        label="Billing Email",
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address for billing',
            'autocomplete': 'email'
        })
    )
    billing_phone = forms.CharField(
        label="Phone (Optional)",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Billing phone number',
            'autocomplete': 'tel'
        })
    )
    billing_street_address1 = forms.CharField(
        label="Street Address 1",
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'House number and street name',
            'autocomplete': 'address-line1'
        })
    )
    billing_street_address2 = forms.CharField(
        label="Street Address 2 (Optional)",
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Apartment,suite, unit etc. (optional)',
            'autocomplete': 'address-line2'
        })
    )
    billing_city = forms.CharField(
        label="City",
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Town or City',
            'autocomplete': 'address-level2'
        })
    )
    billing_postcode = forms.CharField(
        label="Postal Code",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Postal Code (e.g. 90210)',
            'autocomplete': 'postal-code'
        })
    )
    billing_country = CountryField().formfield(
        label="Country",
        required=True,
        initial='PH',
        widget=CountrySelectWidget(attrs={'autocomplete': 'country'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if not self.request or not self.request.user.is_authenticated:
            if 'save_info' in self.fields:
                del self.fields['save_info']

        for field_name, field in self.fields.items():
            if field_name == 'save_info':
                field.widget.attrs['class'] = 'form-check-input'
                continue

            if field_name != 'billing_country':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-select'
            if field.required:
                field.label += '*'

            field.widget.attrs['class'] = 'payment-form-input'
            field.label = ''

    def clean(self):
        cleaned_data = super().clean()

        street_address1 = cleaned_data.get('billing_street_address1')
        street_address2 = cleaned_data.get('billing_street_address2')

        if street_address2 and not street_address1:
            self.add_error(
                'billing_street_address2',
                "Street Address 2 cannot be provided without Street Address 1."
                )

        return cleaned_data

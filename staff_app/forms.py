from django import forms
from trips.models import Trip
from booking.models import (
    Booking,
    BOOKING_STATUS_CHOICES,
    PAYMENT_STATUS_CHOICES,
    REFUND_STATUS_CHOICES,
    PAYMENT_METHOD_CHOICES
    )


class TripForm(forms.ModelForm):
    """
    Form for updating Trip model instances.
    """
    class Meta:
        model = Trip
        fields = [
            'trip_number', 'origin', 'destination', 'date',
            'departure_time', 'arrival_time', 'available_seats',
            'price', 'company_name', 'bus_number',
            'origin_station', 'destination_station'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'type': 'time'}),
            'price': forms.NumberInput(attrs={'min': '1', 'step': '0.01'}),
        }

    def clean_price(self):
        """
        Ensures the 'price' field is a positive value greater than zero.
        """
        price = self.cleaned_data.get('price')

        if price is not None and price <= 0:
            raise forms.ValidationError(
                "The trip price must be a positive value greater than zero \
                (e.g., $1.00)."
            )
        return price

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, (forms.DateInput, forms.TimeInput)):
                field.widget.attrs.pop('size', None)
            if not field.widget.attrs.get('placeholder') and \
                field_name in [
                    'origin',
                    'destination',
                    'trip_number',
                    'company_name',
                    'bus_number',
                    'origin_station',
                    'destination_station'
                    ]:
                field.widget.attrs['placeholder'] = field.label


class BookingForm(forms.ModelForm):
    """
    Form for updating Booking model instances.
    Only 'status' and 'payment_status' are editable by default in this form.
    """
    class Meta:
        model = Booking
        fields = [
            'status',
            'payment_status',
            'refund_status',
        ]
        widgets = {
            'status': forms.Select(choices=BOOKING_STATUS_CHOICES),
            'payment_status': forms.Select(choices=PAYMENT_STATUS_CHOICES),
            'refund_status': forms.Select(choices=REFUND_STATUS_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

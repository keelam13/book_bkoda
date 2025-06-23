from django import forms
from trips.models import Trip


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
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, (forms.DateInput, forms.TimeInput)):
                field.widget.attrs.pop('size', None)
            if not field.widget.attrs.get('placeholder') and field_name in ['origin', 'destination', 'trip_number', 'company_name', 'bus_number', 'origin_station', 'destination_station']:
                field.widget.attrs['placeholder'] = field.label
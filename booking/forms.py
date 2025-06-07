from django import forms
from .models import Booking
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

        print(f"DEBUG FORM: In __init__: Request user authenticated: {self.request.user.is_authenticated if self.request and self.request.user else 'N/A'}")

        if not self.request or not self.request.user.is_authenticated:
            if 'save_info' in self.fields:
                del self.fields['save_info']


        for i in range(self.num_passengers):

            # Define each passenger field with unique names
            self.fields[f'passenger_name{i+1}'] = forms.CharField(
                    max_length=100,
                    required=True,
                    widget=forms.TextInput()
            )
            self.fields[f'passenger_age{i+1}'] = forms.IntegerField(
                    min_value=0,
                    required=False,
                    widget=forms.NumberInput()
            )
            self.fields[f'passenger_email{i+1}'] = forms.EmailField(
                    max_length=255,
                    required=True,
                    widget=forms.EmailInput()
            )
            self.fields[f'passenger_contact_number{i+1}'] = forms.CharField(
                    max_length=20,
                    required=True,
                     widget=forms.TextInput()
            )

        passenger_placeholders = {
            'name': 'Full Name',
            'age': 'Age',
            'email': 'Email Address',
            'contact_number': 'Contact Number',
        }

        for field_name, field_obj in self.fields.items():
            # Handle 'save_info' field separately
            if field_name == 'save_info':
                field_obj.widget.attrs['class'] = 'form-check-input'
                print(f"DEBUG FORM: Styled 'save_info' field.Label is: '{field_obj.label}'")
                continue # Skip general styling for save_info

            # Apply general CSS class to all other fields
            field_obj.widget.attrs['class'] = 'stripe-style-input'
            # Remove labels for all other fields (passenger fields)
            field_obj.label = ''
            print(f"DEBUG FORM: After setting label: Field '{field_name}' label is '{field_obj.label}' (type: {type(field_obj.label)})")
                # Get the base placeholder text
            if field_name.startswith('passenger'):
                # Extract the number and type suffix (e.g., '1', 'name') using regex for robustness
                match = re.match(r'passenger_(.*)(\d+)', field_name)
                if match:
                    passenger_number = int(match.group(2)) # e.g., 1
                    field_type_suffix = match.group(1)    # e.g., 'name'

                    # Get the base placeholder text from the dictionary
                    base_placeholder = passenger_placeholders.get(field_type_suffix, '')

                    # Build the final placeholder string
                    current_placeholder_text = f'{base_placeholder} (Passenger {passenger_number})'
                    print(f"DEBUG FORM: Initial placeholder for {field_name}: '{current_placeholder_text}'")
                    # Add required asterisk if necessary
                    if field_obj.required:
                        current_placeholder_text += ' *' # Use += for string concatenation

                    field_obj.widget.attrs['placeholder'] = current_placeholder_text
                    print(f"DEBUG FORM: Styled passenger field: {field_name} with placeholder '{current_placeholder_text}'")
                else:
                    # Fallback for field names that don't match the expected pattern
                    field_obj.widget.attrs['placeholder'] = "Error: Invalid Name"
                    print(f"DEBUG FORM: Warning: Could not parse passenger field name: {field_name}")
            
            if field_name == 'passenger_name1':
                field_obj.widget.attrs['autofocus'] = True
                print(f"DEBUG FORM: Set autofocus for {field_name}")

        print("DEBUG FORM: Finished field styling loop.")
        print(f"DEBUG FORM: Final fields in form object: {list(self.fields.keys())}")

    def clean(self):
        cleaned_data = super().clean()

        if self.trip and self.trip.available_seats < self.num_passengers:
            self.add_error(None, f"Not enough available seats for {self.num_passengers} passengers. Only {self.trip.available_seats} seats remaining.")

        return cleaned_data
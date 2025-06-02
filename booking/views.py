from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from trips.models import Trip
from .models import Booking
from decimal import Decimal

@login_required
def book_trip(request, trip_id, number_of_passengers):
    """
    View to handle the booking confirmation process.

    This view first validates the number of passengers against
    available seats. If valid, it presents a confirmation form,
    and upon POST, creates the booking and associated passenger records.
    """
    trip = get_object_or_404(Trip, pk=trip_id)
    num_passengers = int(number_of_passengers)


    if num_passengers <= 0:
        messages.error(request, "Number of passengers must be at least 1.")

        return redirect('trips')

    if trip.available_seats < num_passengers:
        messages.error(request, f"Sorry, only {trip.available_seats} seats are available for this trip.")
        # Redirect back to the trip search results or home page
        return redirect('trips')

    # Calculate total price (important for confirmation page)
    # Ensure trip.price is Decimal for accurate calculation
    total_price = trip.price * Decimal(str(num_passengers))

    # --- Handle POST request (form submission) ---
    if request.method == 'POST':
        # Pass trip and num_passengers to the form for dynamic field creation
        form = BookingConfirmationForm(request.POST, trip=trip, num_passengers=num_passengers)
        if form.is_valid():
            # Create the Booking instance
            booking = Booking.objects.create(
                user=request.user,
                trip=trip,
                number_of_passengers=num_passengers,
                total_price=total_price,
                # Initial status, will be updated after payment/confirmation
                status='PENDING',
                payment_status='PENDING'
            )

            # Create Passenger instances using the data from the form
            for i in range(num_passengers):
                passenger_name = form.cleaned_data[f'passenger_name_{i+1}']
                Passenger.objects.create(
                    booking=booking,
                    name=passenger_name
                    # Add other fields like age, gender if your Passenger model has them
                )

            # The Trip's available_seats are automatically updated by the Booking model's save method
            # You don't need to do trip.available_seats -= num_passengers; trip.save() here.

            messages.success(request, f"Booking for {num_passengers} passengers confirmed! Your reference is {booking.booking_reference}.")
            return redirect('booking_success', booking_id=booking.id) # Redirect to a success page

        else:
            # Form is not valid (e.g., passenger names not provided)
            messages.error(request, "Please correct the errors below.")
            # Re-render the form with errors
            context = {
                'form': form,
                'trip': trip,
                'number_of_passengers': num_passengers,
                'total_price': total_price,
            }
            return render(request, 'booking/booking_confirmation.html', context)

    # --- Handle GET request (initial display of the form) ---
    else:
        # Pass trip and num_passengers to the form for dynamic field creation
        form = BookingConfirmationForm(trip=trip, num_passengers=num_passengers)
        context = {
            'form': form,
            'trip': trip,
            'number_of_passengers': num_passengers,
            'total_price': total_price,
        }
        return render(request, 'booking/booking_confirmation.html', context)

# Add your booking_success and my_bookings views here as well, if you haven't already
# For example:
@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_success.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

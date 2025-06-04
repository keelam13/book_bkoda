from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from trips.models import Trip
from .models import Booking, Passenger
from .forms import BookingConfirmationForm
from decimal import Decimal


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
        return redirect('trips')

    total_price = trip.price * Decimal(str(num_passengers))

    if request.method == 'POST':
        form = BookingConfirmationForm(request.POST, trip=trip, num_passengers=num_passengers)
        if form.is_valid():
            booking = Booking.objects.create(
                user=request.user,
                trip=trip,
                number_of_passengers=num_passengers,
                total_price=total_price,
                status='PENDING',
                payment_status='PENDING'
            )

            for i in range(num_passengers):
                passenger_name = form.cleaned_data[f'passenger_name_{i+1}']
                Passenger.objects.create(
                    booking=booking,
                    name=passenger_name
                )

            messages.success(request, f"Booking for {num_passengers} passengers confirmed! Your reference is {booking.booking_reference}.")
            return redirect('booking_success', booking_id=booking.id)

        else:
            messages.error(request, "Please correct the errors below.")
            context = {
                'form': form,
                'trip': trip,
                'number_of_passengers': num_passengers,
                'total_price': total_price,
            }
            return render(request, 'booking/booking_confirmation.html', context)
    else:
        form = BookingConfirmationForm(trip=trip, num_passengers=num_passengers)
        context = {
            'form': form,
            'trip': trip,
            'number_of_passengers': num_passengers,
            'total_price': total_price,
            'stripe_public_key': 'pk_test_51RERfiHxb6VU9KshZoAqQUq5AcgDbRj8dny6bo7yrLln0fdLPOo0gHaqXMoXBxiw8RaMpVA5MLtNt7Odl1IKLsBd00zguHgc8a',
            'client_secret': 'test_client_secret_123',
        }
        return render(request, 'booking/booking_form.html', context)


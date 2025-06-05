from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from trips.models import Trip
from .models import Booking, Passenger
from .forms import BookingConfirmationForm
from decimal import Decimal

import stripe


def book_trip(request, trip_id, number_of_passengers):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    trip = get_object_or_404(Trip, pk=trip_id)
    num_passengers = int(number_of_passengers)


    if num_passengers <= 0:
        messages.error(request, "Number of passengers must be at least 1.")

        return redirect('trips')

    if trip.available_seats < num_passengers:
        messages.error(request, f"Sorry, only {trip.available_seats} seats are available for this trip.")
        return redirect('trips')

    total_price = trip.price * Decimal(str(num_passengers))
    stripe_total = round(total_price * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if request.method == 'POST':
        form = BookingConfirmationForm(request.POST, trip=trip, num_passengers=num_passengers)
        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            booking = Booking.objects.create(
                user=user,
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
            context = {
                'form': form,
                'trip': trip,
                'number_of_passengers': num_passengers,
                'total_price': total_price,
            }
            template = 'booking/booking_form.html'
            messages.success(request, f"Booking for {num_passengers} passengers confirmed! Your reference is {booking.booking_reference}.")
            return render(request, template)

        else:
            messages.error(request, "Please correct the errors below.")
            context = {
                'form': form,
                'trip': trip,
                'number_of_passengers': num_passengers,
                'total_price': total_price,
            }
            return render(request, 'booking/booking_form.html', context)
    else:
        form = BookingConfirmationForm(trip=trip, num_passengers=num_passengers)
        context = {
            'form': form,
            'trip': trip,
            'number_of_passengers': num_passengers,
            'total_price': total_price,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }
        return render(request, 'booking/booking_form.html', context)


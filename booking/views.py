from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from trips.models import Trip
from profiles.models import UserProfile
from .models import Booking, Passenger
from .forms import BookingConfirmationForm
from decimal import Decimal
from datetime import timedelta
import json

import stripe


def book_trip(request, trip_id, number_of_passengers):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    
    trip = get_object_or_404(Trip, pk=trip_id)
    num_passengers = int(number_of_passengers)
    passenger_range = range(1, num_passengers + 1)


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
        metadata={
            'trip_id': trip.trip_id,
            'num_passengers': num_passengers,
            'total_price': str(total_price),
        }
    )

    if request.method == 'POST':
        print(f"DEBUG (Pre-Form): request.POST = {request.POST}")
        form = BookingConfirmationForm(request.POST, trip=trip, num_passengers=num_passengers, request=request)
        payment_method = request.POST.get('payment_method')
        payment_intent_id = request.POST.get('payment_intent_id')

        if form.is_valid():
            print(f"DEBUG (Post-Validation): form.cleaned_data = {form.cleaned_data}")
            user = request.user if request.user.is_authenticated else None
            booking = Booking.objects.create(
                user=user,
                trip=trip,
                number_of_passengers=number_of_passengers,
                total_price=total_price,
                status='PENDING',
                payment_status='PENDING'
            )

            for i in range(num_passengers):
                passenger_name = form.cleaned_data[f'passenger_name{i+1}']
                passenger_age = form.cleaned_data.get(f'passenger_age{i+1}')
                passenger_contact = form.cleaned_data.get(f'passenger_contact_number{i+1}')
                passenger_email = form.cleaned_data.get(f'passenger_email{i+1}')

                Passenger.objects.create(
                    booking=booking,
                    name=passenger_name,
                    age=passenger_age,
                    contact_number=passenger_contact,
                    email=passenger_email
                )

            if request.user.is_authenticated and form.cleaned_data.get('save_info'):
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)

                user_profile.default_name = form.cleaned_data.get('passenger_name1')
                user_profile.default_phone_number = form.cleaned_data.get('passenger_contact_number1')
                user_profile.save()
                print(f"DEBUG: User profile updated for {request.user.username} with name {user_profile.default_name} and phone {user_profile.default_phone_number}")
                messages.info(request, 'First passenger details saved to your profile for future bookings!')
            else:
                messages.error(request, 'First passenger details not saved to your profile. Please check the "Save my info" box if you want to save it for future bookings.')
                print(f"DEBUG: User profile not updated for {request.user.username} as 'save_info' was not checked.")

            if payment_method == 'card':
                if payment_intent_id:
                    try:
                        stripe_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                        if stripe_intent.status == 'succeeded':
                            booking.payment_status = 'PAID'
                            booking.status = 'CONFIRMED'
                            booking.save()
                            messages.success(request, f"Booking confirmed and paid! Reference: {booking.booking_reference}")
                            return redirect('booking_success', booking_id=booking.id)
                        else:
                            messages.error(request, f"Card payment status: {stripe_intent.status}. Please try again or use another method.")
                            booking.payment_status = 'FAILED'
                            booking.save()
                            context = {
                                'form': form,
                                'trip': trip,
                                'num_passengers': num_passengers,
                                'total_price': total_price,
                                'stripe_public_key': stripe_public_key,
                                'client_secret': intent.client_secret,
                            }
                            return render(request, 'booking/booking_form.html', context)

                    except stripe.error.StripeError as e:
                        messages.error(request, f"A Stripe error occurred: {e}")
                        booking.payment_status = 'FAILED'
                        booking.save()

                        context = {
                            'form': form,
                            'trip': trip,
                            'num_passengers': num_passengers,
                            'total_price': total_price,
                            'stripe_public_key': stripe_public_key,
                            'client_secret': intent.client_secret,
                        }
                        return render(request, 'booking/booking_form.html', context)
                else:
                    messages.error(request, "Card payment selected, but Payment Intent ID was not received.")
                    booking.payment_status = 'FAILED'
                    booking.save()

                    context = {
                        'form': form,
                        'trip': trip,
                        'num_passengers': num_passengers,
                        'total_price': total_price,
                        'stripe_public_key': stripe_public_key,
                        'client_secret': intent.client_secret,
                    }
                    return render(request, 'booking/booking_form.html', context)


            elif payment_method == 'other':
                messages.success(request, f"Booking created! Please complete payment via the selected method. Your reference is {booking.booking_reference}.")
                return redirect('booking_success', booking_id=booking.id)

            else:
                messages.error(request, "Invalid payment method selected. Please choose a valid option.")
                booking.payment_status = 'FAILED'
                booking.save()
                context = {
                    'form': form,
                    'trip': trip,
                    'num_passengers': num_passengers,
                    'total_price': total_price,
                    'stripe_public_key': stripe_public_key,
                    'client_secret': intent.client_secret,
                }
                return render(request, 'booking/booking_form.html', context)

        else:
            messages.error(request, "Please correct the errors below.")
            context = {
                'form': form,
                'trip': trip,
                'num_passengers': num_passengers,
                'total_price': total_price,
                'stripe_public_key': stripe_public_key,
                'client_secret': intent.client_secret,
            }
            return render(request, 'booking/booking_form.html', context)

    else:
        form = BookingConfirmationForm(trip=trip, num_passengers=num_passengers)

        if request.user.is_authenticated:
            user_profile = UserProfile.objects.filter(user=request.user).first()

            if user_profile:
                initial_data = {
                    'passenger_name1': request.user.get_full_name() or request.user.username,
                    'passenger_contact_number1': user_profile.default_phone_number,
                    'passenger_email1': request.user.email,
                }
                form = BookingConfirmationForm(initial=initial_data, trip=trip, num_passengers=num_passengers, request=request)

        context = {
            'form': form,
            'trip': trip,
            'num_passengers': num_passengers,
            'passenger_range': passenger_range,
            'total_price': total_price,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }
        return render(request, 'booking/booking_form.html', context)


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    passengers =booking.passengers.all()
    payment_method_chosen = 'card'
    booking_expiry_date = booking.booking_date + timedelta(hours=24)

    context = {
        'booking': booking,
        'trip': booking.trip,
        'passengers': passengers,
        'payment_method_chosen': payment_method_chosen,
        'booking_expiry_date': booking_expiry_date,
    }

    if booking.payment_status == 'PAID' or booking.payment_status == 'CONFIRMED':
        return render(request, 'booking/booking_success.html', context)
    else:
        payment_method_chosen = 'other'
        return render(request, 'booking/booking_pending.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db import transaction

from trips.models import Trip
from profiles.models import UserProfile
from .models import Booking, Passenger
from .forms import BookingConfirmationForm, BillingDetailsForm
from .utils import send_booking_email

from datetime import timedelta
from decimal import Decimal
import stripe


def book_trip(request, trip_id, number_of_passengers):
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

    if request.method == 'POST':
        form = BookingConfirmationForm(request.POST, trip=trip, num_passengers=num_passengers, request=request)

        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            
            with transaction.atomic():
                booking = Booking.objects.create(
                    user=user,
                    trip=trip,
                    number_of_passengers=num_passengers,
                    total_price=total_price,
                    status='PENDING_PAYMENT',
                    payment_status='PENDING'
                )

                for i in range(num_passengers):
                    passenger_data = {
                        'name': form.cleaned_data[f'passenger_name{i+1}'],
                        'age': form.cleaned_data.get(f'passenger_age{i+1}'),
                        'contact_number': form.cleaned_data.get(f'passenger_contact_number{i+1}'),
                        'email': form.cleaned_data.get(f'passenger_email{i+1}')
                    }
                    Passenger.objects.create(booking=booking, **passenger_data)

                trip.available_seats -= num_passengers
                trip.save()

                if request.user.is_authenticated and form.cleaned_data.get('save_info'):
                    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                    user_profile.default_name = form.cleaned_data.get('passenger_name1')
                    user_profile.default_phone_number = form.cleaned_data.get('passenger_contact_number1')
                    user_profile.default_email = form.cleaned_data.get('passenger_email1')
                    user_profile.save()
                    messages.info(request, 'First passenger details saved to your profile for future bookings!')

                if not request.user.is_authenticated:
                    request.session['anonymous_booking_id'] = booking.id
                    request.session.modified = True
                    messages.success(request, f"Your guest booking {booking.booking_reference} created! Please proceed to payment.")
                else:
                    messages.success(request, f"Booking {booking.booking_reference} created! Please proceed to payment.")

                messages.success(request, f"Booking {booking.booking_reference} created! Please proceed to payment.")
                send_booking_email(booking, email_type='pending_payment_instructions', booking_form_data=form.cleaned_data)
                return redirect('process_payment', booking_id=booking.id)
        else:
            messages.error(request, "Please correct the errors below.")
            context = {
                'form': form,
                'trip': trip,
                'num_passengers': num_passengers,
                'passenger_range': passenger_range,
                'total_price': total_price,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            }
            return render(request, 'booking/booking_form.html', context)

    else:
        form = BookingConfirmationForm(trip=trip, num_passengers=num_passengers)

        if request.user.is_authenticated:
            user_profile = UserProfile.objects.filter(user=request.user).first()
            if user_profile:
                initial_data = {
                    'passenger_name1': user_profile.default_name or request.user.username,
                    'passenger_contact_number1': user_profile.default_phone_number,
                    'passenger_email1': user_profile.default_email or request.user.email,
                }
                form = BookingConfirmationForm(initial=initial_data, trip=trip, num_passengers=num_passengers, request=request)

        context = {
            'form': form,
            'trip': trip,
            'num_passengers': num_passengers,
            'passenger_range': passenger_range,
            'total_price': total_price,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'booking/booking_form.html', context)


def process_payment(request, booking_id):
    booking = None

    if request.user.is_authenticated:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    else:
        session_booking_id = request.session.get('anonymous_booking_id')
        if session_booking_id and str(session_booking_id) == str(booking_id):
            booking = get_object_or_404(Booking, id=booking_id)
        else:
            messages.error(request, "Access to this booking is unauthorized or your session has expired. Please start a new booking.")
            return redirect('trips')
        
    if not booking:
        messages.error(request, "Booking not found or not accessible.")
        return redirect('trips')
        
    if booking.payment_status == 'PAID' or booking.status == 'CONFIRMED':
        messages.info(request, "This booking has already been paid or confirmed.")
        return redirect('manage_booking:booking_detail', booking_id=booking.id)
        
    if booking.status == 'CANCELED':
        messages.error(request, "This booking has been cancelled and cannot be paid.")
        return redirect('manage_booking:booking_detail', booking_id=booking.id)

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = round(booking.total_price * 100)

    first_passenger_email = ''
    first_passenger_contact_number = ''
    if booking.passengers.exists():
        first_passenger = booking.passengers.first()
        first_passenger_email = first_passenger.email if first_passenger.email else ''
        first_passenger_contact_number = first_passenger.contact_number if first_passenger.contact_number else ''
    
    intent = None
    billing_form = None
    user_profile = None

    if request.method == 'GET':
        try:
            if booking.stripe_payment_intent_id:
                try:
                    intent = stripe.PaymentIntent.retrieve(booking.stripe_payment_intent_id)
                    if intent.status in ['succeeded', 'canceled']:
                        intent = None
                except stripe.error.InvalidRequestError:
                    intent = None
               
            if not intent:
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                    metadata={
                        'booking_id': str(booking.id),
                        'booking_reference': booking.booking_reference,
                        'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
                    }
                )
                booking.stripe_payment_intent_id = intent.id
                booking.save(update_fields=['stripe_payment_intent_id'])

        except stripe.error.StripeError as e:
            messages.error(request, f"Error preparing payment: {e}. Please try again.")
            return redirect('manage_booking:booking_detail', booking_id=booking.id)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}. Please try again.")
            return redirect('manage_booking:booking_detail', booking_id=booking.id)

        # Initialize billing form for GET request
        if request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            billing_form = BillingDetailsForm(initial={
                'billing_name': user_profile.default_name or request.user.get_full_name() or request.user.username,
                'billing_email': user_profile.default_email or request.user.email,
                'billing_phone': user_profile.default_phone_number,
                'billing_street_address1': user_profile.default_street_address1,
                'billing_street_address2': user_profile.default_street_address2,
                'billing_city': user_profile.default_city,
                'billing_postcode': user_profile.default_postcode,
                'billing_country': user_profile.default_country,
            })
        else:
            billing_form = BillingDetailsForm(initial={
                'billing_name': booking.passengers.first().name if booking.passengers.exists() else '',
                'billing_email': first_passenger_email,
                'billing_phone': first_passenger_contact_number,
            })

    # Handle payment submission (POST request)
    if request.method == 'POST':
        selected_payment_method = request.POST.get('selected_payment_method_hidden')
        payment_intent_id = request.POST.get('payment_intent_id')
        billing_form = BillingDetailsForm(request.POST)
        save_info = request.POST.get('save_info') == 'on'

        if selected_payment_method == 'card':
            if not payment_intent_id:
                messages.error(request, "Card payment selected, but Payment Intent ID was not received. Please try again.")
                booking.payment_status = 'FAILED'
                booking.save()
                return redirect('process_payment', booking_id=booking.id)
            
            try:
                stripe_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                if stripe_intent.status == 'succeeded':
                    with transaction.atomic():
                        booking.payment_status = 'PAID'
                        booking.status = 'CONFIRMED'
                        booking.stripe_payment_intent_id = stripe_intent.id
                        booking.payment_method_type = 'CARD'

                        if stripe_intent.payment_method:
                            pm = stripe.PaymentMethod.retrieve(stripe_intent.payment_method)
                            if pm.type == 'card':
                                booking.card_brand = pm.card.brand
                                booking.card_last4 = pm.card.last4
                            booking.stripe_payment_method_id = pm.id

                        booking.save()

                        # --- Update UserProfile default address if requested ---
                        if request.user.is_authenticated and save_info:
                            try:
                                user_profile, created = UserProfile.objects.get_or_create(user=request.user) 
                                if billing_form.is_valid():
                                    user_profile.default_name = billing_form.cleaned_data['billing_name']
                                    user_profile.default_email = billing_form.cleaned_data['billing_email']
                                    user_profile.default_phone_number = billing_form.cleaned_data['billing_phone']
                                    user_profile.default_street_address1 = billing_form.cleaned_data['billing_street_address1']
                                    user_profile.default_street_address2 = billing_form.cleaned_data['billing_street_address2']
                                    user_profile.default_city = billing_form.cleaned_data['billing_city']
                                    user_profile.default_postcode = billing_form.cleaned_data['billing_postcode']
                                    user_profile.default_country = billing_form.cleaned_data['billing_country']
                                    user_profile.save()
                                    messages.info(request, 'Billing details saved to your profile.')
                                else:
                                    messages.warning(request, "Could not save billing details to profile due to invalid data.")
                            except UserProfile.DoesNotExist:
                                messages.error(request, f"Error: UserProfile does not exist for authenticated user {request.user.id} during profile save.")

                        if not request.user.is_authenticated and 'anonymous_booking_id' in request.session:
                            del request.session['anonymous_booking_id']
                            request.session.modified = True

                        messages.success(request, f"Payment successful! Booking {booking.booking_reference} is now confirmed.")
                        return redirect('booking_success', booking_id=booking.id)

                else:
                    messages.error(request, f"Card payment status: {stripe_intent.status}. Please try again or use another method.")
                    booking.payment_status = 'FAILED'
                    booking.save()
                    return redirect('process_payment', booking_id=booking.id)

            except stripe.error.StripeError as e:
                messages.error(request, f"A Stripe error occurred: {e}. Please try again.")
                booking.payment_status = 'FAILED'
                booking.save()
                return redirect('process_payment', booking_id=booking.id)

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}. Please try again.")
                booking.payment_status = 'FAILED'
                booking.save()
                return redirect('process_payment', booking_id=booking.id)

        elif selected_payment_method in ['CASH', 'GCASH']:
            with transaction.atomic():
                booking.status = 'PENDING_PAYMENT'
                booking.payment_status = 'PENDING'
                booking.payment_method_type = selected_payment_method
                booking.save()

            if not request.user.is_authenticated and 'anonymous_booking_id' in request.session:
                del request.session['anonymous_booking_id']
                request.session.modified = True
            
            messages.info(request, f"Booking {booking.booking_reference} received! Please complete your {selected_payment_method} payment at designated centers within 24 hours.")
            return redirect('booking_success', booking_id=booking.id)

        else:
            messages.error(request, "Invalid payment method selected. Please choose a valid option.")
            return redirect('process_payment', booking_id=booking.id)

    context = {
        'booking': booking,
        'amount_due': booking.total_price,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret if intent else None,
        'first_passenger_email': first_passenger_email,
        'first_passenger_contact_number': first_passenger_contact_number,
        'billing_form': billing_form,
        'user_profile': user_profile,
    }
    return render(request, 'booking/payment_page.html', context)
    

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    passengers = booking.passengers.all()

    booking_expiry_date = None
    if booking.booking_date:
        booking_expiry_date = booking.booking_date + timedelta(hours=24)

    context = {
        'booking': booking,
        'trip': booking.trip,
        'passengers': passengers,
        'booking_expiry_date': booking_expiry_date,
    }

    if booking.payment_status == 'PAID' and booking.status == 'CONFIRMED':
        return render(request, 'booking/booking_success.html', context)
    else:
        return render(request, 'booking/booking_pending.html', context)
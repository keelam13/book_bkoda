from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from trips.models import Trip
from my_account.models import UserProfile
from .models import Booking, Passenger, BookingPolicy, PAYMENT_METHOD_CHOICES
from .forms import BookingConfirmationForm, BillingDetailsForm
from .utils import send_booking_email

from datetime import datetime, timedelta
from decimal import Decimal
import stripe

# --- Helper Functions for Reusability ---
def _get_booking_policy():
    """Retrieves or creates the standard booking policy."""
    try:
        booking_policy = BookingPolicy.objects.get(name="Standard Booking Policy")
    except BookingPolicy.DoesNotExist:
        booking_policy = BookingPolicy.objects.first()
        if not booking_policy:
            booking_policy = BookingPolicy.objects.create(name="Standard Booking Policy")
    return booking_policy

def _get_payment_method_context(trip_or_booking):
    """
    Determines available payment methods and related cutoff information.
    Takes either a Trip object or a Booking object.
    """
    booking_policy = _get_booking_policy()

    if isinstance(trip_or_booking, Trip):
        trip_date = trip_or_booking.date
        departure_time = trip_or_booking.departure_time
    elif isinstance(trip_or_booking, Booking):
        trip_date = trip_or_booking.trip.date
        departure_time = trip_or_booking.trip.departure_time
    else:
        raise ValueError("Invalid object type for _get_payment_method_context")

    trip_datetime_naive = datetime.combine(trip_date, departure_time)
    trip_datetime_aware = timezone.make_aware(trip_datetime_naive, timezone.get_current_timezone())
    time_until_departure = trip_datetime_aware - timezone.now()

    offline_payment_cutoff_hours = booking_policy.offline_payment_cutoff_hours_before_departure
    offline_payment_cutoff_seconds = offline_payment_cutoff_hours * 3600

    available_payment_methods = list(PAYMENT_METHOD_CHOICES)
    is_offline_payment_disallowed = False

    if time_until_departure < timedelta(hours=offline_payment_cutoff_hours):
        available_payment_methods = [('CARD', 'Card')]
        is_offline_payment_disallowed = True

    return {
        'available_payment_methods': available_payment_methods,
        'offline_payment_cutoff_hours': offline_payment_cutoff_hours,
        'offline_payment_cutoff_seconds': offline_payment_cutoff_seconds,
        'time_until_departure': time_until_departure,
        'is_offline_payment_disallowed': is_offline_payment_disallowed,
    }

def _get_initial_billing_details(request, booking=None):
    """Helper to get initial data for BillingDetailsForm."""
    initial_data = {}

    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        return {
            'billing_name': user_profile.default_name or request.user.get_full_name() or request.user.username,
            'billing_email': user_profile.default_email or request.user.email,
            'billing_phone': user_profile.default_phone_number,
            'billing_street_address1': user_profile.default_street_address1,
            'billing_street_address2': user_profile.default_street_address2,
            'billing_city': user_profile.default_city,
            'billing_postcode': user_profile.default_postcode,
            'billing_country': user_profile.default_country,
        }
    elif booking and booking.passengers.exists():
        first_passenger = booking.passengers.first()
        return {
            'billing_name': first_passenger.name,
            'billing_email': first_passenger.email,
            'billing_phone': first_passenger.contact_number,
        }
    if 'billing_country' not in initial_data or not initial_data['billing_country']:
        initial_data['billing_country'] = 'PH'

    return {}


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

    payment_context = _get_payment_method_context(trip)
    if payment_context['is_offline_payment_disallowed']:
        messages.warning(request, f"For bookings within {payment_context['offline_payment_cutoff_hours']} hours of departure, only Card payments are accepted to ensure immediate confirmation.")

    if request.method == 'POST':
        form = BookingConfirmationForm(request.POST, trip=trip, num_passengers=num_passengers, request=request)

        if form.is_valid():
            selected_payment_method_on_form = request.POST.get('payment_method_type')

            # if selected_payment_method_on_form in ['CASH', 'GCASH'] and payment_context['is_offline_payment_disallowed']:
            #     messages.error(request, f"Cash/GCash payments are not allowed for trips departing within {payment_context['offline_payment_cutoff_hours']} hours. Please select Card payment.")
                
            #     context = {
            #         'form': form,
            #         'trip': trip,
            #         'num_passengers': num_passengers,
            #         'passenger_range': passenger_range,
            #         'total_price': total_price,
            #         'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            #         **payment_context,
            #     }
            #     return render(request, 'booking/booking_form.html', context)

            with transaction.atomic():
                user = request.user if request.user.is_authenticated else None
                booking = Booking.objects.create(
                    user=user,
                    trip=trip,
                    number_of_passengers=num_passengers,
                    total_price=total_price,
                    status='PENDING_PAYMENT',
                    payment_status='PENDING',
                    payment_method_type=selected_payment_method_on_form,
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
                    messages.success(request, f"Your guest booking {booking.booking_reference} created! Please proceed to payment.")
                else:
                    messages.success(request, f"Booking {booking.booking_reference} created! Please proceed to payment.")

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
                **payment_context,
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

        template = 'booking/booking_form.html'
        context = {
            'form': form,
            'trip': trip,
            'num_passengers': num_passengers,
            'passenger_range': passenger_range,
            'total_price': total_price,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            **payment_context,
        }
        return render(request, template, context)


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

    payment_context = _get_payment_method_context(booking)

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
        billing_form = BillingDetailsForm(
            initial=_get_initial_billing_details(request, booking),
            request=request)
        if request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Handle payment submission (POST request)
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cancel_booking':
            if booking.status == 'CANCELED':
                messages.info(request, f"Booking {booking.booking_reference} is already canceled.")
                return redirect('home')

            with transaction.atomic():
                original_status = booking.status
                booking.status = 'CANCELED'
                booking.payment_status = 'REFUNDED' if booking.payment_status == 'PAID' else 'NONE'
                booking.save()

                if not request.user.is_authenticated and 'anonymous_booking_id' in request.session:
                    del request.session['anonymous_booking_id']
                    request.session.modified = True

            messages.success(request, f"Booking {booking.booking_reference} has been successfully canceled.")
            send_booking_email(booking, email_type='cancellation')
            return redirect('home')

        elif action == 'confirm_payment':
            if booking.payment_status == 'PAID' or booking.status == 'CONFIRMED':
                messages.info(request, "This booking has already been paid or confirmed.")
                return redirect('manage_booking:booking_detail', booking_id=booking.id)

            if booking.status == 'CANCELED':
                messages.error(request, "This booking has been cancelled and cannot be paid.")
                return redirect('manage_booking:booking_detail', booking_id=booking.id)

        selected_payment_method = request.POST.get('selected_payment_method_hidden')
        payment_intent_id = request.POST.get('payment_intent_id')
        billing_form = BillingDetailsForm(request.POST, request=request)
        save_info = request.POST.get('save_info') == 'on'

        billing_form_is_valid = billing_form.is_valid()

        if selected_payment_method == 'CARD':
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

                        if request.user.is_authenticated and save_info:
                            try:
                                user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                                if billing_form_is_valid:
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
                            except Exception as e:
                                messages.error(request, f"Error saving billing details to profile: {e}")

                        if not request.user.is_authenticated and 'anonymous_booking_id' in request.session:
                            del request.session['anonymous_booking_id']

                        messages.success(request, f"Payment successful! Booking {booking.booking_reference} is now confirmed.")
                        send_booking_email(booking, email_type='booking_confirmation')
                        return redirect('booking_success', booking_id=booking.id)

                else:
                    messages.error(request, f"Card payment status: {stripe_intent.status}. Please try again or use another method.")
                    booking.payment_status = 'FAILED'
                    booking.save()
            except stripe.error.StripeError as e:
                messages.error(request, f"A Stripe error occurred: {e}. Please try again.")
                booking.payment_status = 'FAILED'
                booking.save()
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}. Please try again.")
                booking.payment_status = 'FAILED'
                booking.save()

        elif selected_payment_method in ['CASH', 'GCASH']:
            if payment_context['is_offline_payment_disallowed']:
                messages.error(request, f"Cash/GCash payments are not allowed for trips departing within {payment_context['offline_payment_cutoff_hours']} hours. Please select Card payment.")
            else:
                with transaction.atomic():
                    booking.status = 'PENDING_PAYMENT'
                    booking.payment_status = 'PENDING'
                    booking.payment_method_type = selected_payment_method
                    booking.stripe_payment_intent_id = None
                    booking.save()

                if not request.user.is_authenticated and 'anonymous_booking_id' in request.session:
                    del request.session['anonymous_booking_id']

                messages.info(request, f"Booking {booking.booking_reference} received! Please complete your {selected_payment_method} payment at designated centers within 24 hours.")
                send_booking_email(booking, email_type='pending_payment_instructions')
                return redirect('booking_success', booking_id=booking.id)
        else:
            messages.error(request, "Invalid payment method selected. Please choose a valid option.")

    template = 'booking/payment_page.html'
    context = {
        'booking': booking,
        'trip': booking.trip,
        'total_price': booking.total_price,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret if intent else None,
        'num_passsengers': booking.number_of_passengers,
        'first_passenger_email': first_passenger_email,
        'first_passenger_contact_number': first_passenger_contact_number,
        'billing_form': billing_form,
        'user_profile': user_profile if request.user.is_authenticated else None,
        **payment_context,
    }
    return render(request, template, context)


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    passengers = booking.passengers.all()

    booking_expiry_date = None
    if booking.booking_date:
        booking_expiry_date = booking.booking_date + timedelta(hours=24)

    user_is_authenticated = request.user.is_authenticated

    context = {
        'booking': booking,
        'trip': booking.trip,
        'passengers': passengers,
        'booking_expiry_date': booking_expiry_date,
        'user_is_authenticated': user_is_authenticated,
    }

    if booking.payment_status == 'PAID' and booking.status == 'CONFIRMED':
        return render(request, 'booking/booking_success.html', context)
    else:
        return render(request, 'booking/booking_pending.html', context)
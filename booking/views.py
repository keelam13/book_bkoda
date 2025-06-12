from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from trips.models import Trip
from profiles.models import UserProfile
from .models import Booking, Passenger
from .forms import BookingConfirmationForm

from datetime import timedelta
from decimal import Decimal
import stripe


# --- Helper Function for Email Sending (remains largely the same) ---
def send_booking_email(booking, email_type, booking_form_data=None):
    subject = ''
    template_name = ''

    user = booking.user if booking.user else None
    recipient_email = user.email if user and user.email else None
    if not recipient_email and booking.passengers.exists():
        recipient_email = booking.passengers.first().email

    if not recipient_email and booking_form_data and booking_form_data.get('passenger_email1'):
        recipient_email = booking_form_data.get('passenger_email1')

    if not recipient_email:
        print(f"Warning: No recipient email found for booking {booking.booking_reference}. Email not sent.")
        return

    if email_type == 'initial_booking_pending_payment_email':
        subject = f"Booking Received (Action Required) - Trip {booking.booking_reference}"
        template_name = 'emails/initial_booking_pending_payment_email.html'
    elif email_type == 'payment_receipt':
        subject = f"Payment Confirmed - Your Trip Booking {booking.booking_reference}"
        template_name = 'emails/payment_receipt_email.html'
    elif email_type == 'other_payment_instructions':
        subject = f"Booking Created (Action Required) - Trip {booking.booking_reference}"
        template_name = 'emails/other_payment_instructions_email.html'
    else:
        print(f"Warning: Unknown email type '{email_type}' requested for booking {booking.booking_reference}")
        return

    context = {
        'booking': booking,
        'user': user,
        'trip': booking.trip,
        'passengers': booking.passengers.all(),
        'total_price': booking.total_price,
        'payment_status': booking.get_payment_status_display(),
        'booking_status': booking.get_status_display(),
    }

    html_message = render_to_string(template_name, context)
    plain_message = f"Dear {user.username if user else 'Customer'},\n\n"
    if email_type == 'payment_receipt':
        plain_message += f"Your payment of Php{booking.total_price} for booking {booking.booking_reference} has been received and your booking is confirmed.\n"
    elif email_type == 'initial_booking_pending_payment':
        plain_message += f"Your booking {booking.booking_reference} has been created and is pending payment.\n"
    elif email_type == 'other_payment_instructions':
         plain_message += f"Your booking {booking.booking_reference} has been created. Please complete payment via the selected method.\n"
    plain_message += "Thank you for booking with us!\n"

    try:
        email = EmailMessage(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
        )
        email.content_subtype = "html"
        email.send()
        print(f"Email '{email_type}' for booking {booking.booking_reference} sent to terminal for {recipient_email}.")
    except Exception as e:
        print(f"Failed to send email '{email_type}' for booking {booking.booking_reference} to {recipient_email}: {e}")


@login_required
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

                messages.success(request, f"Booking {booking.booking_reference} created! Please proceed to payment.")
                
                send_booking_email(booking, email_type='initial_booking_pending_payment_email', booking_form_data=form.cleaned_data)

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
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'booking/booking_form.html', context)


@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.payment_status == 'PAID' or booking.status == 'CONFIRMED':
        messages.info(request, "This booking has already been paid or confirmed.")
        return redirect('manage_booking:booking_detail', booking_id=booking.id)
    
    if booking.status == 'CANCELLED':
        messages.error(request, "This booking has been cancelled and cannot be paid.")
        return redirect('manage_booking:booking_detail', booking_id=booking.id)

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    stripe_total = round(booking.total_price * 100)

    first_passenger_email = ''
    first_passenger_contact_number = ''
    if booking.passengers.exists():
        first_passenger = booking.passengers.first()
        first_passenger_email = first_passenger.email if first_passenger.email else ''
        first_passenger_contact_number = first_passenger.contact_number if first_passenger.contact_number else ''
        print(f"1st Passsenger name : {first_passenger}")

    try:
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={
                'booking_id': str(booking.id),
                'booking_reference': booking.booking_reference,
                'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
            }
        )
    except stripe.error.StripeError as e:
        messages.error(request, f"Error creating payment intent: {e}")
        return redirect('manage_booking:booking_detail', booking_id=booking.id)

    if request.method == 'POST':
        payment_method = request.POST.get('selected_payment_method_hidden')
        payment_intent_id = request.POST.get('payment_intent_id')

        if payment_method == 'card':
            if payment_intent_id:
                try:
                    stripe_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                    if stripe_intent.status == 'succeeded':
                        with transaction.atomic():
                            booking.payment_status = 'PAID'
                            booking.status = 'CONFIRMED'
                            booking.stripe_payment_intent_id = stripe_intent.id
                            booking.save()

                        messages.success(request, f"Payment successful! Booking {booking.booking_reference} is now confirmed.")
                        send_booking_email(booking, email_type='payment_receipt')
                        return redirect('booking_success', booking_id=booking.id)
                    else:
                        messages.error(request, f"Card payment status: {stripe_intent.status}. Please try again or use another method.")
                        booking.payment_status = 'FAILED'
                        booking.save()

                        context = {
                            'booking': booking,
                            'amount_due': booking.total_price,
                            'stripe_public_key': stripe_public_key,
                            'client_secret': intent.client_secret,
                            'errors': True
                        }
                        return render(request, 'booking/payment_page.html', context)

                except stripe.error.StripeError as e:
                    messages.error(request, f"A Stripe error occurred: {e}. Please try again.")
                    booking.payment_status = 'FAILED'
                    booking.save()

                    context = {
                        'booking': booking,
                        'amount_due': booking.total_price,
                        'stripe_public_key': stripe_public_key,
                        'client_secret': intent.client_secret,
                        'errors': True
                    }
                    return render(request, 'booking/payment_page.html', context)
            else:
                messages.error(request, "Card payment selected, but Payment Intent ID was not received. Please try again.")
                booking.payment_status = 'FAILED'
                booking.save()

                context = {
                    'booking': booking,
                    'amount_due': booking.total_price,
                    'stripe_public_key': stripe_public_key,
                    'client_secret': intent.client_secret,
                    'errors': True
                }
                return render(request, 'booking/payment_page.html', context)

        elif payment_method == 'other':
            booking.status = 'PENDING_PAYMENT'
            booking.payment_status = 'PENDING'
            booking.save()

            messages.success(request, f"Booking created! Please complete payment via the selected method. Your reference is {booking.booking_reference}.")
            send_booking_email(booking, email_type='other_payment_instructions')
            return redirect('booking_success', booking_id=booking.id)

        else:
            messages.error(request, "Invalid payment method selected. Please choose a valid option.")

            context = {
                'booking': booking,
                'amount_due': booking.total_price,
                'stripe_public_key': stripe_public_key,
                'client_secret': intent.client_secret,
                'first_passenger_email': first_passenger_email,
                'first_passenger_contact_number': first_passenger_contact_number,
                'errors': True
            }
            return render(request, 'booking/payment_page.html', context)

    else:
        context = {
            'booking': booking,
            'amount_due': booking.total_price,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
            'first_passenger_email': first_passenger_email,
            'first_passenger_contact_number': first_passenger_contact_number,
            'errors': True
        }
        print(f"1st Passenger email: {first_passenger_email}")
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
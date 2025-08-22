from django.db import transaction
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from booking.models import Booking, BookingPolicy
from booking.utils import send_booking_email
from decimal import Decimal
from datetime import datetime

import stripe


def _calculate_reschedule_financials(original_booking, new_trip, policy):
    """
    Calculates the financial implications of a reschedule.
    Assumes the number of passengers remains the same as the original booking.
    """
    policy = BookingPolicy.objects.first()
    num_passengers = original_booking.number_of_passengers

    original_total_price = original_booking.total_price
    original_base_price = original_booking.trip.price
    new_total_price_base = new_trip.price * num_passengers
    new_total_price_base = new_total_price_base.quantize(Decimal('0.01'))
    fare_difference = new_total_price_base - original_base_price
    rescheduling_charge = Decimal('0.00')
    reschedule_type_message = ""

    time_until_departure = original_booking.original_departure_time - timezone.now()
    time_until_original_departure = time_until_departure.total_seconds() / 3600

    if time_until_original_departure > policy.free_rescheduling_cutoff_hours:
        reschedule_type_message = "Free Reschedule"
    elif time_until_original_departure >= policy.late_rescheduling_cutoff_hours:
        reschedule_type_message = "Late Reschedule"
        rescheduling_charge = original_total_price * policy.late_rescheduling_charge_percentage
        rescheduling_charge = rescheduling_charge.quantize(Decimal('0.01'))
    else:
        reschedule_type_message = "Not Allowed (too close to departure)"

    total_due_or_refund = fare_difference + rescheduling_charge

    amount_to_pay = Decimal('0.00')
    amount_to_refund = Decimal('0.00')

    if total_due_or_refund > 0:
        amount_to_pay = total_due_or_refund
    elif total_due_or_refund < 0:
        amount_to_refund = abs(total_due_or_refund)

    return {
        'original_total_price': original_total_price,
        'original_base_price': original_base_price,
        'new_total_price_base': new_total_price_base,
        'fare_difference': fare_difference,
        'rescheduling_charge': rescheduling_charge,
        'amount_to_pay': amount_to_pay,
        'amount_to_refund': amount_to_refund,
        'reschedule_type_message': reschedule_type_message,
        'time_until_original_departure': time_until_original_departure,
        'num_passengers': num_passengers
    }


def _calculate_cancellation_financials(booking, policy):
    """
    Calculates the refund amount and type for a booking cancellation.
    Returns a dictionary of financial details.
    """
    if booking.is_rescheduled and booking.original_departure_time:
        departure_datetime = booking.original_departure_time
    else:
        departure_datetime = timezone.make_aware(datetime.combine(booking.trip.date, booking.trip.departure_time))

    current_time = timezone.now()
    time_until_departure_hours = (departure_datetime - current_time).total_seconds() / 3600

    refund_amount = Decimal('0.00')
    refund_type_message = "N/A"
    can_proceed = True
    cancellation_fee_rate = policy.late_cancellation_fee_percentage

    if time_until_departure_hours > policy.free_cancellation_cutoff_hours:
        refund_amount = booking.total_price  # Full refund
        refund_type_message = "FULL"
    elif time_until_departure_hours >= policy.late_cancellation_cutoff_hours:
        refund_amount = booking.total_price * (1 - cancellation_fee_rate)
        refund_type_message = f"{int((1 - cancellation_fee_rate) * 100)}% (due to late cancellation fee)"
    else:
        refund_amount = Decimal('0.00')  # No refund
        refund_type_message = f"NONE (less than {policy.late_cancellation_cutoff_hours} hours before departure)"

    return {
        'can_proceed': can_proceed,
        'refund_amount': refund_amount,
        'refund_type_message': refund_type_message,
        'time_until_departure_hours': time_until_departure_hours,
    }


def _create_new_rescheduled_booking(request, original_booking, new_trip, new_booking_params):
    """
    Handles the common transactional logic for a successful reschedule.

    Returns a redirect response or raises an exception on failure.
    """
    num_passengers = original_booking.number_of_passengers
    
    original_booking.status = 'RESCHEDULED'
    original_booking.save(update_fields=['status'])

    new_booking = Booking.objects.create(
        user=original_booking.user,
        trip=new_trip,
        original_trip=original_booking.trip,
        number_of_passengers=num_passengers,
        booking_reference=f"R-{original_booking.booking_reference}",
        is_rescheduled=True,
        original_departure_time=original_booking.original_departure_time,
        **new_booking_params
    )

    for passenger in original_booking.passengers.all():
        passenger.pk = None
        passenger.booking = new_booking
        passenger.save()

    original_booking.trip.available_seats += original_booking.number_of_passengers
    original_booking.trip.save()
    new_trip.available_seats -= num_passengers
    new_trip.save()

    return new_booking


def _process_refund_for_reschedule(request, original_booking, new_trip, amount_to_refund):
    """
    Processes a refund for a booking reschedule and updates the original booking.
    
    This function should be called within a transaction.

    STRIPE_MOCK_REFUNDS is used to simulate refund processing in development.
    """
    if original_booking.stripe_payment_intent_id:
        if settings.STRIPE_MOCK_REFUNDS:
            messages.success(request, f"REFUND of Php{amount_to_refund:.2f} is being processed. Please check your email for more details.")
            send_booking_email(original_booking, email_type='pending_refund')
            original_booking.refund_status = 'COMPLETED'
            original_booking.refund_amount = amount_to_refund
            original_booking.save(update_fields=['refund_status', 'refund_amount'])
        # Added for future development
        else:
            stripe_refund_amount_cents = round(amount_to_refund * 100)
            try:
                refund = stripe.Refund.create(
                    payment_intent=original_booking.stripe_payment_intent_id,
                    amount=stripe_refund_amount_cents,
                    metadata={
                        'booking_id': str(original_booking.id),
                        'new_trip_id': str(new_trip.id),
                        'refund_for_reschedule': 'true',
                    }
                )
                if refund.status == 'succeeded':
                    original_booking.refund_status = 'COMPLETED'
                    original_booking.refund_amount = amount_to_refund
                    messages.success(request, f"Refund of Php{amount_to_refund:.2f} processed successfully via Stripe.")
                    original_booking.save(update_fields=['refund_status', 'refund_amount'])
                else:
                    original_booking.refund_status = 'PENDING'
                    original_booking.refund_amount = amount_to_refund
                    original_booking.save(update_fields=['refund_status', 'refund_amount'])
                    messages.warning(request, f"Stripe refund status: {refund.status}. It may still be processing or require review.")
            except stripe.error.StripeError as e:
                original_booking.refund_status = 'FAILED'
                original_booking.save(update_fields=['refund_status'])
                raise Exception(f"A Stripe error occurred during refund processing: {e}")
    else:
        original_booking.refund_status = 'PENDING'
        original_booking.refund_amount = amount_to_refund
        original_booking.save(update_fields=['refund_status', 'refund_amount'])
        send_booking_email(original_booking, email_type='pending_refund')
        messages.info(request, f"Your booking is rescheduled. A refund of Php{amount_to_refund:.2f} is pending manual processing. Please check your email for instructions.")


def _process_refund_for_cancellation(request, booking, refund_amount, refund_type_message):
    """
    Handles the transactional part of a booking cancellation, including refund processing.
    Assumes this function is called from within a transaction.
    """

    if booking.stripe_payment_intent_id:
        if settings.STRIPE_MOCK_REFUNDS:
            messages.success(request, f'REFUND of Php{refund_amount} is being processed. An email is sent for more details.')
            send_booking_email(booking, email_type='refund_processing')
            booking.refund_status = 'COMPLETED'
            booking.refund_amount = refund_amount
        else:
            stripe_refund_amount_cents = round(refund_amount * 100)
            try:
                refund = stripe.Refund.create(
                    payment_intent=booking.stripe_payment_intent_id,
                    amount=stripe_refund_amount_cents,
                    metadata={
                        'booking_id': str(booking.id),
                        'booking_reference': booking.booking_reference,
                        'refund_type': refund_type_message,
                    }
                )
                if refund.status == 'succeeded':
                    booking.refund_status = 'COMPLETED'
                    booking.refund_amount = refund_amount
                    messages.success(request, f"Refund of Php{refund_amount:.2f} processed successfully via Stripe.")
                else:
                    booking.refund_status = 'PENDING'
                    messages.warning(request, f"Stripe refund status: {refund.status}. It may still be processing or require review. We will inform you once it's complete.")
            except stripe.error.StripeError as e:
                booking.refund_status = 'FAILED'
                booking.save()
                raise Exception(f"A Stripe error occurred during refund processing: {e}")
    else:
        booking.refund_status = 'PENDING'
        booking.refund_amount = refund_amount
        send_booking_email(booking, email_type='refund_processing')
        messages.info(request, f"Your booking is cancelled. A refund of Php{refund_amount:.2f} is pending manual processing (non-card payment).")
   
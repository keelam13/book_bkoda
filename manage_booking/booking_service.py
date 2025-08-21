from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from booking.models import Booking, BookingPolicy
from booking.utils import send_booking_email
from decimal import Decimal


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




def _create_new_rescheduled_booking(request, original_booking, new_trip, new_booking_params):
    """
    Handles the common transactional logic for a successful reschedule.

    Returns a redirect response or raises an exception on failure.
    """
    num_passengers = original_booking.number_of_passengers
    
    try:
        with transaction.atomic():
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

    except Exception as e:
        messages.error(request, f"An error occurred during the reschedule: {e}")
        raise

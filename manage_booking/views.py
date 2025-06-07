from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from booking.models import Booking
from trips.models import Trip
from django.db.models import Prefetch
from django.utils import timezone
from datetime import datetime, timedelta


@login_required
def booking_list(request):
    """
    Displays a list of all bookings for the currently logged-in user.
    """
    user_bookings = Booking.objects.filter(
        user=request.user
    ).prefetch_related(
        'passengers'
    ).order_by('-booking_date')

    context = {
        'bookings': user_bookings,
        'title': 'My Bookings'
    }
    return render(request, 'manage_booking/booking_list.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    Displays detailed information for a specific booking.
    Ensures the booking belongs to the logged-in user.
    Calculates if cancellation/rescheduling is allowed based on precise policy.
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers', 'trip'),
        pk=booking_id,
        user=request.user
    )

    can_cancel = False
    can_reschedule = False
    cancellation_fee_applied = False
    rescheduling_charge_applied = False

    eligible_status_for_action = (
        booking.status == 'CONFIRMED' and booking.payment_status == 'PAID'
    )

    if booking.trip.date and booking.trip.departure_time:
        departure_datetime_naive = datetime.combine(booking.trip.date, booking.trip.departure_time)

        departure_datetime = timezone.make_aware(departure_datetime_naive)
        
        current_time = timezone.now()

        time_until_departure = departure_datetime - current_time

        if eligible_status_for_action:
            if time_until_departure > timedelta(hours=24):
                # Free cancellation/rescheduling
                can_cancel = True
                can_reschedule = True
                messages.info(request, "Cancellation and rescheduling are free if done more than 24 hours before departure.")
            elif time_until_departure > timedelta(hours=3): # Within 24 hours down to 3 hours
                # Cancellation with 50% fee
                can_cancel = True
                cancellation_fee_applied = True
                messages.info(request, "Cancellation within 24 to 3 hours before departure incurs a 50% fee.")
                
                # Rescheduling with 15% charge
                can_reschedule = True
                rescheduling_charge_applied = True
                messages.info(request, "Rescheduling within 24 to 3 hours before departure incurs a 15% charge.")
                
            else: # Less than 3 hours until departure
                messages.warning(request, "Cancellation is no longer allowed (less than 3 hours before departure).")
                messages.warning(request, "Rescheduling is no longer allowed (less than 3 hours before departure).")

        else:
            messages.info(request, "This booking cannot be modified due to its current status or payment status.")


    else:
        messages.error(request, "Departure date or time is missing for this trip, unable to determine modification eligibility.")

    context = {
        'booking': booking,
        'title': f'Booking #{booking.booking_reference}',
        'can_cancel': can_cancel,
        'can_reschedule': can_reschedule,
        'cancellation_fee_applied': cancellation_fee_applied,
        'rescheduling_charge_applied': rescheduling_charge_applied,
    }
    return render(request, 'manage_booking/booking_detail.html', context)

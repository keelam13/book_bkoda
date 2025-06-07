from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from booking.models import Booking
from trips.models import Trip
from django.db.models import Prefetch
from django.utils import timezone
from datetime import timedelta


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
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers', 'trip'),
        pk=booking_id,
        user=request.user
    )

    can_cancel = False
    can_reschedule = False

    if booking.status in ['PENDING', 'CONFIRMED', 'PAYMENT_PROCESSING'] and booking.payment_status in ['PENDING', 'PAID', 'PROCESSING']:
        if booking.trip.date and booking.trip.date > (timezone.now().date() + timedelta(hours=24)):
            can_cancel = True
            can_reschedule = True
        else:
            messages.info(request, "Cancellation or rescheduling is not allowed within 24 Hours of the trip start date.")
    else:
        messages.info(request, "This booking cannot be modified due to its current status.")


    context = {
        'booking': booking,
        'title': f'Booking #{booking.booking_reference}',
        'can_cancel': can_cancel,
        'can_reschedule': can_reschedule,
    }
    return render(request, 'manage_booking/booking_detail.html', context)

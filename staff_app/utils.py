from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking


def get_all_abandoned_bookings():
    """
    Returns a dictionary of QuerySets for and calculate counts of null, departed, and unpaid bookings.
    """
    cutoff_time_null = timezone.now() - timedelta(hours=1)
    null_bookings_queryset = Booking.objects.filter(
        Q(payment_method_type__isnull=True) | Q(payment_method_type=''),
        status='PENDING_PAYMENT',
        booking_date__lt=cutoff_time_null
    )
    null_count = null_bookings_queryset.count()

    now = timezone.now()
    departed_bookings_queryset = Booking.objects.filter(
        Q(trip__date__lt=now.date()) | Q(trip__date=now.date(), trip__departure_time__lt=now.time()),
        status='PENDING_PAYMENT'
    )
    departed_count = departed_bookings_queryset.count()

    cutoff_time_unpaid = timezone.now() - timedelta(hours=24)
    unpaid_bookings_queryset = Booking.objects.filter(
        status='PENDING_PAYMENT',
        payment_status='PENDING',
        booking_date__lt=cutoff_time_unpaid
    )
    unpaid_count = unpaid_bookings_queryset.count()

    return {
        'null_bookings': null_bookings_queryset,
        'null_count': null_count,
        'departed_bookings': departed_bookings_queryset,
        'departed_count': departed_count,
        'unpaid_bookings': unpaid_bookings_queryset,
        'unpaid_count': unpaid_count,
    }

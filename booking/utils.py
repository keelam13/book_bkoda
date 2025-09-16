from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Q

from my_account.models import UserProfile
from trips.models import Trip
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)


def send_booking_email(booking, email_type, booking_form_data=None, **kwargs):
    subject = ''
    html_template_name = ''

    user = booking.user if booking.user else None
    recipient_email = user.email if user and user.email else None

    if not recipient_email and booking.passengers.exists():
        recipient_email = booking.passengers.first().email

    if not recipient_email and booking_form_data and booking_form_data.get(
        'passenger_email1'
    ):
        recipient_email = booking_form_data.get('passenger_email1')

    customer_name = 'Valued Customer'
    if booking.passengers.exists():
        customer_name = booking.passengers.first().name
    elif user and user.get_full_name():
        customer_name = user.get_full_name()
    elif user and user.username:
        customer_name = user.username

    if email_type == 'pending_payment_instructions':
        subject = (
            f"Your Booking is Pending Payment -"
            f"Reference: {booking.booking_reference}"
        )
        html_template_name = 'emails/pending_payment_email.html'
    elif email_type == 'payment_receipt':
        subject = f"Payment Receipt for Booking {booking.booking_reference}"
        html_template_name = 'emails/payment_receipt_email.html'
    elif email_type == 'booking_confirmation':
        subject = (
            f"Your Booking is Confirmed! Reference:"
            f"{booking.booking_reference}"
        )
        html_template_name = 'emails/booking_confirmation_email.html'
    elif email_type == 'cancellation_unpaid':
        subject = (
            f'Booking {booking.booking_reference} Has Been Cancelled (Unpaid)')
        html_template_name = 'emails/cancellation_unpaid_email.html'
        if 'reason' not in kwargs:
            kwargs['reason'] = (
                f'Your booking was automatically cancelled'
                f'because payment was not received within 24 hours.'
            )
    elif email_type == 'cancellation':
        subject = (
            f'Your Booking {booking.booking_reference} Has Been Cancelled')
        html_template_name = 'emails/cancellation_email.html'
    elif email_type == 'refund_processing':
        subject = f"Refund Processing for Booking {booking.booking_reference}"
        html_template_name = 'emails/refund_processing_email.html'
    elif email_type == 'rescheduled_confirmation':
        subject = (
            f"Your Booking {booking.booking_reference} Has Been Rescheduled!")
        html_template_name = 'emails/rescheduled_confirmation_email.html'

        return

    context = {
        'booking': booking,
        'user': user,
        'trip': booking.trip,
        'passengers': booking.passengers.all(),
        'total_price': booking.total_price,
        'payment_status': booking.get_payment_status_display(),
        'booking_status': booking.get_status_display(),
        'customer_name': customer_name,
        **kwargs,
    }

    html_content = render_to_string(html_template_name, context)

    plain_content = strip_tags(html_content)

    try:
        email = EmailMultiAlternatives(
            subject,
            plain_content,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        logger.error(
            f"Failed to send email '{email_type}' for booking"
            f"{booking.booking_reference} to {recipient_email}: {e}"),
        exc_info = True


def _get_booking_policy():
    """Retrieves or creates the standard booking policy."""
    from .models import BookingPolicy
    try:
        booking_policy = BookingPolicy.objects.get(
            name="Standard Booking Policy"
            )
    except BookingPolicy.DoesNotExist:
        booking_policy = BookingPolicy.objects.first()
        if not booking_policy:
            booking_policy = BookingPolicy.objects.create(
                name="Standard Booking Policy"
                )
    return booking_policy


def _get_payment_method_context(trip_or_booking):
    """
    Determines available payment methods and related cutoff information.
    Takes either a Trip object or a Booking object.
    """
    from .models import Booking, PAYMENT_METHOD_CHOICES
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
    trip_datetime_aware = timezone.make_aware(
        trip_datetime_naive,
        timezone.get_current_timezone()
        )
    time_until_departure = trip_datetime_aware - timezone.now()

    offline_payment_cutoff_hours =\
        booking_policy.offline_payment_cutoff_hours_before_departure
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
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user
            )
        return {
            'billing_name':
                user_profile.default_name or
                request.user.get_full_name() or request.user.username,
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
    if 'billing_country' not in initial_data or\
            not initial_data['billing_country']:
        initial_data['billing_country'] = 'PH'

    return {}


def _get_pending_booking(request):
    """
    Helper function to check for an existing pending booking.

    Checks for pending bookings for both authenticated and anonymous users.
    Returns the pending booking object or None if no pending booking is found.
    """
    from .models import Booking
    now = timezone.now()
    pending_booking = None
    if request.user.is_authenticated:
        pending_booking = Booking.objects.filter(
            Q(trip__date__gt=now.date()) |
            Q(trip__date=now.date(), trip__departure_time__gte=now.time()),
            user=request.user,
            status='PENDING_PAYMENT',
            payment_method_type__isnull=True
        ).first()
    elif 'anonymous_booking_id' in request.session:
        try:
            booking_id = request.session['anonymous_booking_id']
            pending_booking = Booking.objects.get(
                Q(trip__date__gt=now.date()) |
                Q(trip__date=now.date(), trip__departure_time__gte=now.time()),
                id=booking_id,
                status='PENDING_PAYMENT',
                payment_method_type__isnull=True
            )
        except Booking.DoesNotExist:
            del request.session['anonymous_booking_id']

    return pending_booking

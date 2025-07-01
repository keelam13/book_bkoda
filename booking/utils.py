from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import logging

logger = logging.getLogger(__name__)

# --- Helper Function for Email Sending (remains largely the same) ---
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

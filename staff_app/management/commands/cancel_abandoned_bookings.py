from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking
from booking.utils import send_booking_email
from django.db import transaction
from staff_app.utils import get_all_abandoned_bookings


class Command(BaseCommand):
    """
    Django management command to cancel various types of abandoned bookings.

    1. Cancels unpaid bookings that are more than 1 hour old.
    2. Cancels pending bookings for trips that have already departed.
    3. Cancels unpaid bookings older than 24 hours.
    """
    help = 'Cancels all abandoned bookings based on their status and trip \
        departure.'

    def handle(self, *args, **options):

        abandoned_bookings = get_all_abandoned_bookings()

        # --- Task 1: Cancel old, null-payment bookings ---
        null_bookings = abandoned_bookings['null_bookings']
        null_count = abandoned_bookings['null_count']

        if null_count > 0:
            try:
                with transaction.atomic():
                    updated_null_count = null_bookings.update(
                        status='CANCELLED',
                        payment_status='FAILED',
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully cancelled {updated_null_count} old,"
                        f"null-payment booking(s). "))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"An error occurred while cancelling old null"
                        f"bookings: {e}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "No old, null-payment bookings found to cancel."))

        # --- Task 2: Cancel pending bookings for past trips ---
        departed_bookings = abandoned_bookings['departed_bookings']
        departed_count = abandoned_bookings['departed_count']

        if departed_count > 0:
            try:
                with transaction.atomic():
                    updated_departed_count = departed_bookings.update(
                        status='CANCELLED',
                        payment_status='FAILED',
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully cancelled {updated_departed_count}"
                        f"departed pending booking(s). "))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"An error occurred while cancelling departed"
                        f"bookings: {e}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "No departed pending bookings found to cancel."))

        # --- Task 3: Cancel unpaid bookings older than 24 hours ---
        unpaid_bookings = abandoned_bookings['unpaid_bookings']
        unpaid_count = abandoned_bookings['unpaid_count']

        if unpaid_count > 0:
            try:
                with transaction.atomic():
                    updated_unpaid_count = unpaid_bookings.update(
                        status='CANCELLED',
                        payment_status='FAILED',
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully cancelled {updated_unpaid_count}"
                        f"unpaid booking(s). "))
                send_booking_email(
                    unpaid_bookings, email_type='cancellation_unpaid')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"An error occurred while cancelling unpaid"
                        f"bookings: {e}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "No unpaid bookings found to cancel."))

        self.stdout.write(self.style.SUCCESS("Finished cleanup process."))

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking
from booking.utils import send_booking_email
from django.db import transaction


class Command(BaseCommand):
    """
    Django management command to cancel various types of abandoned bookings.

    1. Cancels unpaid bookings that are more than 1 hour old.
    2. Cancels pending bookings for trips that have already departed.
    3. Cancels unpaid bookings older than 24 hours.
    """
    help = 'Cancels all abandoned bookings based on their status and trip departure.'

    def handle(self, *args, **options):

        # --- Task 1: Cancel old, null-payment bookings ---
        cutoff_time = timezone.now() - timedelta(hours=1)
        null_bookings = Booking.objects.filter(
            Q(payment_method_type__isnull=True) | Q(payment_method_type=''),
            status='PENDING_PAYMENT',
            booking_date__lt=cutoff_time
        )

        null_count = null_bookings.count()

        if null_count > 0:
            try:
                with transaction.atomic():
                    updated_null_count = null_bookings.update(
                        status='CANCELLED', 
                        payment_status='FAILED',
                    )
                self.stdout.write(self.style.SUCCESS(f"Successfully cancelled {updated_null_count} old, null-payment booking(s)."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred while cancelling old null bookings: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("No old, null-payment bookings found to cancel."))

        # --- Task 2: Cancel pending bookings for past trips ---
        now = timezone.now()
        departed_bookings = Booking.objects.filter(
            Q(trip__date__lt=now.date()) | Q(trip__date=now.date(), trip__departure_time__lt=now.time()),
            status='PENDING_PAYMENT'
        )
        departed_count = departed_bookings.count()
        
        if departed_count > 0:
            try:
                with transaction.atomic():
                    updated_departed_count = departed_bookings.update(
                        status='CANCELLED', 
                        payment_status='FAILED',
                    )
                self.stdout.write(self.style.SUCCESS(f"Successfully cancelled {updated_departed_count} departed pending booking(s)."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred while cancelling departed bookings: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("No departed pending bookings found to cancel."))

        # --- Task 3: Cancel unpaid bookings older than 24 hours ---
        cutoff_time_unpaid = timezone.now() - timedelta(hours=24)
        unpaid_bookings = Booking.objects.filter(
            status='PENDING_PAYMENT',
            payment_status='PENDING',
            booking_date__lt=cutoff_time_unpaid
        )
        unpaid_count = unpaid_bookings.count()
        
        if unpaid_count > 0:
            try:
                with transaction.atomic():
                    updated_unpaid_count = unpaid_bookings.update(
                        status='CANCELLED', 
                        payment_status='FAILED',
                    )
                self.stdout.write(self.style.SUCCESS(f"Successfully cancelled {updated_unpaid_count} unpaid booking(s)."))
                send_booking_email(unpaid_bookings, email_type='cancellation_unpaid')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred while cancelling unpaid bookings: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("No unpaid bookings found to cancel."))

        self.stdout.write(self.style.SUCCESS("Finished cleanup process."))
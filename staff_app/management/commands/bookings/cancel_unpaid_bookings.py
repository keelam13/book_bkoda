from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking
from booking.utils import send_booking_email
from django.db import transaction


class Command(BaseCommand):
    help = 'Cancels unpaid bookings that are older than 24 hours.'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(hours=24)

        unpaid_bookings = Booking.objects.filter(
            status='PENDING_PAYMENT',
            payment_status='PENDING',
            booking_date__lt=cutoff_time
        )

        if not unpaid_bookings.exists():
            self.stdout.write(self.style.SUCCESS('No unpaid bookings found for cancellation.'))
            return

        cancelled_count = 0
        for booking in unpaid_bookings:
            try:
                with transaction.atomic():
                    booking.status = 'CANCELED'
                    booking.payment_status = 'FAILED'
                    booking.save()

                    send_booking_email(booking, email_type='cancellation_unpaid')
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully cancelled booking: {booking.booking_reference} '
                        f'created on {booking.booking_date} (Expired).'
                    ))
                    cancelled_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error cancelling booking {booking.booking_reference}: {e}'
                ))
                # You might want to log this to an error monitoring system

        self.stdout.write(self.style.SUCCESS(
            f'Finished cancellation process. Total cancelled: {cancelled_count}'
        ))


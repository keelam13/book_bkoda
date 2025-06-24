from django.db import models, transaction
from django.contrib.auth.models import User
from trips.models import Trip
from decimal import Decimal
from datetime import datetime
from .utils import send_booking_email

BOOKING_STATUS_CHOICES = [
    ('PENDING_PAYMENT', 'Pending Payment'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELED', 'Canceled'),
    ('COMPLETED', 'Completed'),
    ('CANCELLATION_FAILED', 'Cancellation Failed'),
]

PAYMENT_STATUS_CHOICES = [
    ('PENDING', 'Pending Payment'),
    ('PAID', 'Paid'),
    ('REFUNDED', 'Refunded'),
    ('FAILED', 'Payment Failed'),
]

REFUND_STATUS_CHOICES = [
    ('NONE', 'No Refund Made'),
    ('PENDING', 'Refund Pending'),
    ('COMPLETED', 'Refund Completed'),
    ('FAILED', 'Refund Failed'),
]

PAYMENT_METHOD_CHOICES = [
    ('CARD', 'Card'),
    ('CASH', 'Cash'),
    ('GCASH', 'GCash'),
]

class Booking(models.Model):
    """
    Represents a reservation made by a user for a trip.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    number_of_passengers = models.PositiveIntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='PENDING_PAYMENT'
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )

    refund_status = models.CharField(
        max_length=20,
        help_text="Status of any refunds associated with this booking.",
        choices=REFUND_STATUS_CHOICES,
        default='NONE',
    )
    
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount refunded for this booking."
    )

    booking_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    payment_method_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=PAYMENT_METHOD_CHOICES,
        help_text="Type of payment method (e.g., Card, Cash, GCash, Bank Transfer)."
    )
    card_brand = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Brand of the card used (e.g., 'Visa', 'Mastercard', 'Amex')."
    )
    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        help_text="Last four digits of the card used."
    )
    stripe_payment_method_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID of the Stripe PaymentMethod object used for this booking."
    )

    class Meta:
        ordering = ['-booking_date']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def save(self, *args, **kwargs):
        """
        Overrides the save method to handle:
        1. Storing original status for comparison.
        2. Generating booking reference (if new).
        3. Updating trip's available seats based on status changes.
        4. Triggering confirmation/receipt emails on status transition to PAID/CONFIRMED.
        """
        is_new_booking = not self.pk
        original_payment_status = None
        original_booking_status = None
        original_num_passengers = 0

        if not is_new_booking:
            try:
                original_booking = Booking.objects.get(pk=self.pk)
                original_payment_status = original_booking.payment_status
                original_booking_status = original_booking.status
                original_num_passengers = original_booking.number_of_passengers
            except Booking.DoesNotExist:
                pass

        if is_new_booking:
            if self.status in ['PENDING', 'CONFIRMED']:
                if self.trip.available_seats is not None:
                    self.trip.available_seats -= self.number_of_passengers
                    self.trip.save()
                else:
                    print("WARNING: Trip available_seats is null, cannot subtract seats.")
        elif original_booking:
            if self.number_of_passengers != original_num_passengers:
                passenger_diff = self.number_of_passengers - original_booking.number_of_passengers
                if self.trip.available_seats is not None:
                    self.trip.available_seats -= passenger_diff
                    self.trip.save()
                else:
                    print("WARNING: Trip available_seats is null, cannot adjust seats on passenger count change.")

            if self.status == 'CANCELED' and original_booking_status != 'CANCELED':
                if self.trip.available_seats is not None:
                    self.trip.available_seats += self.number_of_passengers
                    self.trip.save(update_fields=['available_seats'])
                else:
                    print("WARNING: Trip available_seats is null, cannot return seats on cancellation.")

        super().save(*args, **kwargs)

        if is_new_booking and not self.booking_reference:
            user_identifier = self.user.id if self.user else "ANON"
            trip_identifier = self.trip.pk
            self.booking_reference = (
                f"BKODA-{user_identifier}-{trip_identifier}-{self.pk}-"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            super().save(update_fields=['booking_reference'])

       # --- Email Sending Logic (after final save) ---
        is_now_paid_and_confirmed = (self.payment_status == 'PAID' and self.status == 'CONFIRMED')
        was_not_paid_and_confirmed_before = (
            original_payment_status != 'PAID' or original_booking_status != 'CONFIRMED'
        )

        if is_now_paid_and_confirmed and was_not_paid_and_confirmed_before:
            transaction.on_commit(lambda: send_booking_email(self, 'payment_receipt'))
            transaction.on_commit(lambda: send_booking_email(self, 'booking_confirmation'))

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"Booking {self.booking_reference or 'N/A'} for {user_display} on {self.trip}"


class Passenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        booking_ref_display = self.booking.booking_reference or 'N/A'
        return f"{self.name} (Booking: {booking_ref_display})"
    

class BookingPolicy(models.Model):
    """
    Defines the rules for booking cancellation and rescheduling.
    """
    name = models.CharField(max_length=100, unique=True, default="Standard Booking Policy")
    description = models.TextField(blank=True, help_text="A description of this policy.")

    # Cancellation Policy Rules
    free_cancellation_cutoff_hours = models.PositiveIntegerField(
        default=24,
        help_text="Hours before departure for free cancellation (e.g., 24 means >24h)."
    )
    late_cancellation_cutoff_hours = models.PositiveIntegerField(
        default=3,
        help_text="Hours before departure after which no refund is issued for cancellation (e.g., 3 means <=3h)."
    )
    late_cancellation_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.50'),
        help_text="Percentage of total price charged for late cancellation (e.g., 0.50 for 50%)."
    )

    # Rescheduling Policy Rules
    free_rescheduling_cutoff_hours = models.PositiveIntegerField(
        default=24,
        help_text="Hours before departure for free rescheduling (e.g., 24 means >24h)."
    )
    late_rescheduling_cutoff_hours = models.PositiveIntegerField(
        default=3,
        help_text="Hours before departure after which rescheduling is not allowed (e.g., 3 means <=3h)."
    )
    late_rescheduling_charge_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.15'),
        help_text="Percentage of total price charged for late rescheduling (e.g., 0.15 for 15%)."
    )

    # Offline payment cutoff
    offline_payment_cutoff_hours_before_departure = models.PositiveIntegerField(
        default=6,
        help_text="Hours before trip departure after which only instant payment methods (e.g., Card) are allowed."
    )

    class Meta:
        verbose_name_plural = "Booking Policies"

    def __str__(self):
        return self.name
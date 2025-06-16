from django.db import models
from django.contrib.auth.models import User
from trips.models import Trip
from decimal import Decimal
from datetime import datetime


class Booking(models.Model):
    """
    Represents a reservation made by a user for a trip.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    number_of_passengers = models.PositiveBigIntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('CANCELED', 'Canceled'),
            ('COMPLETED', 'Completed'),
            ('CANCELLATION_FAILED', 'Cancellation Failed'),
        ],
        default='PENDING'
    )
    payment_status = models.CharField(
        max_length=30,
        choices=[
            ('PENDING', 'Pending Payment'),
            ('PAID', 'Paid'),
            ('REFUNDED', 'Refunded'),
            ('FAILED', 'Payment Failed'),
        ],
        default='PENDING'
    )
    refund_status = models.CharField(
        max_length=20,
        help_text="Status of any refunds associated with this booking.",
        choices=[
            ('NONE', 'No Refund Made'),
            ('PENDING', 'Refund Pending'),
            ('COMPLETED', 'Refund Completed'),
            ('FAILED', 'Refund Failed'),
        ],
        default='NONE',
    )
    
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total amount refunded for this booking."
    )

    booking_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    PAYMENT_METHOD_CHOICES = [
        ('CARD', 'Card'),
        ('CASH', 'Cash'),
        ('GCASH', 'GCash'),
        ('BANK_TRANSFER', 'Bank_Transfer')
    ]

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

    def save(self, *args, **kwargs):
        """
        Overrides the save method to update trip's available seats
        and generate booking reference.
        """
        is_new_booking = not self.pk
        original_booking = None

        if not is_new_booking:
            try:
                original_booking = Booking.objects.get(pk=self.pk)
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
            if self.number_of_passengers != original_booking.number_of_passengers:
                passenger_diff = self.number_of_passengers - original_booking.number_of_passengers
                if self.trip.available_seats is not None:
                    if passenger_diff > 0:
                        self.trip.available_seats -= passenger_diff
                    else:
                        self.trip.available_seats += abs(passenger_diff)
                    self.trip.save()
                else:
                    print("WARNING: Trip available_seats is null, cannot adjust seats on passenger count change.")

        super().save(*args, **kwargs)

        if is_new_booking and not self.booking_reference:
            user_identifier = self.user.id if self.user else "ANON"
            trip_identifier = self.trip.pk
            self.booking_reference = (
                f"BKODA-{user_identifier}-{trip_identifier}-{self.pk}-"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            super().save(update_fields=['booking_reference'])


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
        default=Decimal('0.50'), # 0.50 for 50%
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
        default=Decimal('0.15'), # 0.15 for 15%
        help_text="Percentage of total price charged for late rescheduling (e.g., 0.15 for 15%)."
    )

    class Meta:
        verbose_name_plural = "Booking Policies"

    def __str__(self):
        return self.name
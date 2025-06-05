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
            ('CANCELLED', 'Cancelled'),
            ('COMPLETED', 'Completed'),
        ],
        default='PENDING'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('REFUNDED', 'Refunded'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    booking_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to update trip's available seats
        and generate booking reference.
        """
        is_new_booking = not self.pk

        if is_new_booking:
            if self.status in ['PENDING', 'CONFIRMED']:
                self.trip.update_available_seats(self.number_of_passengers, 'subtract')
                self.trip.save()
        else:
            try:
                original_booking = Booking.objects.get(pk=self.pk)
                original_passengers = original_booking.number_of_passengers
                passenger_diff = self.number_of_passengers - original_passengers
                if passenger_diff != 0:
                    if passenger_diff > 0:
                        self.trip.update_available_seats(passenger_diff, 'subtract')
                    else:
                        self.trip.update_available_seats(abs(passenger_diff), 'add')
                    self.trip.save()
            except Booking.DoesNotExist:

                pass

        super().save(*args, **kwargs)

        if is_new_booking and not self.booking_reference:
            user_identifier = self.user.id if self.user else "ANON"

            trip_identifier = self.trip.pk

            self.booking_reference = (
                f"BKODA-{user_identifier}-{trip_identifier}-{self.pk}-"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            self.save(update_fields=['booking_reference'])


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
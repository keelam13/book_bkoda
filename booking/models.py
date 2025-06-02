from django.db import models
from django.contrib.auth.models import User
from trips.models import Trip
from decimal import Decimal


class Booking(models.Model):
    """
    Represents a reservation made by a user for a trip.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    booking_reference = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
            """
            Overrides the save method to update trip's available seats
            and generate booking reference.
            """
            if not self.booking_reference:
                self.booking_reference = f"BKODA-{self.user.id}-{self.trip.id}-{self.booking_date.strftime('%Y%m%d%H%M%S')}"

            if self.pk:
                original_passengers = Booking.objects.get(pk=self.pk).number_of_passengers
                passenger_diff = self.number_of_passengers - original_passengers
                if passenger_diff != 0:
                    if passenger_diff > 0:
                        self.trip.update_available_seats(passenger_diff, 'subtract')
                    else:
                        self.trip.update_available_seats(abs(passenger_diff), 'add')
            else:
                if self.status in ['PENDING', 'CONFIRMED']:
                    self.trip.update_available_seats(self.number_of_passengers, 'subtract')

            super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_reference} for {self.user.username} on {self.trip}"

from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class Trip(models.Model):
    """
    Represents a trip with details like origin, destination, date, time,
    and seat availability.
    """
    trip_id = models.AutoField(primary_key=True)
    trip_number = models.CharField(max_length=30, db_index=True)
    origin = models.CharField(max_length=30, db_index=True)
    destination = models.CharField(max_length=30, db_index=True)
    date = models.DateField(db_index=True)
    departure_time = models.TimeField(
        help_text="Expected departure time (HH:MM)"
    )
    arrival_time = models.TimeField(
        help_text="Expected arrival time (HH:MM)"
    )
    available_seats = models.IntegerField()
    price = models.DecimalField(
        max_digits=10,
        null=False,
        blank=False,
        decimal_places=2,
        default=0.00)
    company_name = models.CharField(
        max_length=100, default='BKODA Transport')
    bus_number = models.CharField(max_length=50, blank=True, null=True)
    origin_station = models.CharField(max_length=255, blank=True, null=True)
    destination_station = models.CharField(
        max_length=255, blank=True, null=True)

    def clean(self):
        """
        Validation for model fields.
        """
        # Ensures the price is not a negative value
        if self.price is not None and self.price < 0:
            raise ValidationError(
                {'price': 'The trip price cannot be a negative value.'}
            )

        # Ensures available seats are not negative
        if self.available_seats is not None and self.available_seats < 0:
            raise ValidationError(
                {'available_seats': 'Available seats cannot be negative.'}
            )

        super().clean()

    def save(self, *args, **kwargs):
        """
        Overrides save to explicitly call full_clean() to ensure
        the model's clean() method (which validates the price) runs 
        before the data is saved to the database.
        """
        self.full_clean() 
        super().save(*args, **kwargs)

    def update_available_seats(
            self, number_of_passengers, operation='subtract'):
        """
        Updates the available seats for the trip.
        """
        if operation == 'subtract':
            self.available_seats -= number_of_passengers
        elif operation == 'add':
            self.available_seats += number_of_passengers
        self.save()

    @property
    def duration(self):
        """
        Calculates the duration of the trip in 'Xh Ym' format.
        Assumes arrival time can be on the next day if earlier than departure
        time.
        """
        if self.departure_time and self.arrival_time:
            dummy_date = datetime.min.date()
            dt_departure = datetime.combine(dummy_date, self.departure_time)
            dt_arrival = datetime.combine(dummy_date, self.arrival_time)

            if dt_arrival < dt_departure:
                dt_arrival += timedelta(days=1)

            time_diff = dt_arrival - dt_departure
            total_seconds = int(time_diff.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes:02d}m"
        return "N/A"

    def __str__(self):
        """
        Returns a string representation of the trip.
        """
        return (
            f"Trip {self.trip_number}:"
            f"From {self.origin} to {self.destination} "
            f"on {self.date} from {self.departure_time} to "
            f"{self.arrival_time} - Price: {self.price}"
        )

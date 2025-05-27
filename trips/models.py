from django.db import models


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
    time = models.TimeField()
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()

    def update_available_seats(self, number_of_seats, operation='subtract'):
        """
        Updates the available seats for the trip.

        Args:
            number_of_seats (int): The number of seats to add or subtract.
            operation (str): 'subtract' to decrease seats, 'add' to increase
            seats. Defaults to 'subtract'.
        """
        if operation == 'subtract':
            self.available_seats -= number_of_seats
        elif operation == 'add':
            self.available_seats += number_of_seats
        self.save()

    def __str__(self):
        """
        Returns a string representation of the trip.
        """
        return (
            f"{self.trip_number}: {self.origin} to {self.destination}"
            f"({self.date} {self.time})"
        )
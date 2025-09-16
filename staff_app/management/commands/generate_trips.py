from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, time, date
from random import choice
from trips.models import Trip


class Command(BaseCommand):
    """
    Generates sample trips for the next 5 days, starting from the day after
    the latest trip date.

    This command creates 5 trips per day for both "Kabayan-Baguio" and
    "Baguio-Kabayan" routes, using predefined time intervals and ensuring
    unique trip times for each route per day.
    """

    help = 'Generates sample trips'

    def handle(self, *args, **options):
        """
        Handles the generation of sample trips.

        Retrieves the latest trip date, calculates the end date (14 days
        from the start date), and generates trips for each day within the
        range.
        """

        latest_trip = Trip.objects.order_by('-date').first()

        if latest_trip:
            start_date = latest_trip.date + timedelta(days=1)
        else:
            start_date = date.today()

        num_days_to_generate = 5
        end_date = start_date + timedelta(days=num_days_to_generate - 1)

        time_intervals = [time(hour) for hour in range(6, 16, 2)]

        current_date = start_date

        while current_date <= end_date:
            used_times_kb = set()
            used_times_bk = set()

            # Kabayan to Baguio
            for _ in range(5):
                try:
                    trip_time = self.get_unique_time(
                        time_intervals, used_times_kb)
                    used_times_kb.add(trip_time)
                    available_seats = 12
                    price = 250.00
                    Trip.objects.create(
                        origin="Kabayan, Benguet",
                        destination="Baguio City",
                        date=current_date,
                        departure_time=trip_time,
                        available_seats=available_seats,
                        price=price,
                        trip_number=(
                            f'KAB-BAG-{current_date.strftime("%Y%m%d")}'
                            f'-{trip_time.strftime("%H%M")}'),
                        arrival_time=(
                            datetime.combine(
                                current_date,
                                trip_time) + timedelta(hours=3)).time(),
                        company_name="BKODA Transport",
                    )
                except ValueError as e:
                    break

            # Baguio to Kabayan
            for _ in range(5):
                try:
                    trip_time = self.get_unique_time(
                        time_intervals, used_times_bk)
                    used_times_bk.add(trip_time)
                    total_number_of_seats = 12
                    available_seats = total_number_of_seats
                    price = 250.00
                    Trip.objects.create(
                        origin="Baguio City",
                        destination="Kabayan, Benguet",
                        date=current_date,
                        departure_time=trip_time,
                        available_seats=available_seats,
                        price=price,
                        trip_number=(
                            f'BAG-KAB-{current_date.strftime("%Y%m%d")}'
                            f'-{trip_time.strftime("%H%M")}'),
                        arrival_time=(
                            datetime.combine(
                                current_date,
                                trip_time) + timedelta(hours=3)).time(),
                        company_name="BKODA Transport",
                    )
                except ValueError as e:
                    break

            current_date += timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Trip generation from {start_date} to {end_date}"
                f"completed successfully!"))

    def get_unique_time(self, time_intervals, used_times):
        """
        Gets a unique time from the available time intervals.

        Ensures that the selected time has not been used for the current
        route and date.
        """
        available_times = [t for t in time_intervals if t not in used_times]
        if not available_times:
            raise ValueError(
                "All time intervals have been used for this date. \
                Cannot generate more unique trips.")
        return choice(available_times)

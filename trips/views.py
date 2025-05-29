# your_app/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Trip


def find_trip(request):
    """
    Handles trip search and displays the list of available trips.

    Retrieves search parameters from GET requests, filters trips based
    on origin, destination, and date, calculates total price, and renders the trip list.
    """
    context = {}
    requested_origin = request.GET.get('origin')
    requested_destination = request.GET.get('destination')
    requested_date_str = request.GET.get('date')
    requested_num_travelers_str = request.GET.get('num_travelers')
    today = datetime.now().date()
    now = datetime.now()

    number_of_passengers = 1
    if requested_num_travelers_str:
        try:
            number_of_passengers = int(requested_num_travelers_str)
            if number_of_passengers <= 0:
                messages.error(request, "Number of passengers must be a positive number.")
                return render(request, 'home/index.html', context)
        except ValueError:
            messages.error(request, "Invalid number of passengers. Please enter a whole number.")
            return render(request, 'home/index.html', context)
    else:
        messages.info(request, "Defaulting to 1 passenger for trip search.")
        pass


    if requested_date_str and requested_origin and requested_destination:
        try:
            requested_date = datetime.strptime(
                requested_date_str, '%Y-%m-%d'
                ).date()
            previous_day = requested_date - timedelta(days=1)
            next_day = requested_date + timedelta(days=1)

            trip_list_queryset = Trip.objects.filter(
                origin__icontains=requested_origin,
                destination__icontains=requested_destination,
                date=requested_date
            )

            # Filter out past trips AND prepare for price calculation
            final_trip_list = []
            for trip in trip_list_queryset:
                trip_datetime = datetime.combine(trip.date, trip.time)

                if trip_datetime >= now:
                    calculated_total_price = trip.price * Decimal(number_of_passengers)
                    calculated_total_price = calculated_total_price.quantize(Decimal('0.01'))

                    trip.total_display_price = calculated_total_price
                    trip.requested_passengers = number_of_passengers

                    final_trip_list.append(trip)

            final_trip_list = sorted(final_trip_list, key=lambda trip: trip.time)


            if len(final_trip_list) > 0:
                context = {
                    'trip_list': final_trip_list,
                    'origin': requested_origin,
                    'destination': requested_destination,
                    'current_day': requested_date,
                    'previous_day': previous_day,
                    'next_day': next_day,
                    'number_of_passengers': number_of_passengers,
                }
                return render(request, 'trips/trips.html', context)
            elif requested_date < today:
                messages.error(
                    request, "Sorry, the date you requested is in the past."
                )
            else:
                messages.error(
                    request, "Sorry, there are no trips available yet."
                )
        except ValueError:
            messages.error(
                request, "Invalid date format. Please use YYYY-MM-DD."
            )
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")


    origins = Trip.objects.values_list('origin', flat=True).distinct()
    destinations = Trip.objects.values_list(
        'destination', flat=True
    ).distinct()
    context['origins'] = origins
    context['destinations'] = destinations
    context['search_error'] = messages.get_messages(request)
    return render(request, 'home/index.html', context)
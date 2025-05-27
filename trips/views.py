from django.shortcuts import render
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Trip


def find_trip(request):
    """
    Handles trip search and displays the list of available trips.

    Retrieves search parameters from GET requests, filters trips based
    on origin, destination, and date, and renders the trip list.
    """
    context = {}
    requested_origin = request.GET.get('origin')
    requested_destination = request.GET.get('destination')
    requested_date_str = request.GET.get('date')
    today = datetime.now().date()
    now = datetime.now()

    if requested_date_str and requested_origin and requested_destination:
        try:
            requested_date = datetime.strptime(
                requested_date_str, '%Y-%m-%d'
                ).date()
            previous_day = requested_date - timedelta(days=1)
            next_day = requested_date + timedelta(days=1)

            trip_list = Trip.objects.filter(
                origin__icontains=requested_origin,
                destination__icontains=requested_destination,
                date=requested_date
            )

            # Filter out past trips
            trip_list = [trip for trip in trip_list if datetime.combine(
                trip.date, trip.time
                ) >= now]
            trip_list = sorted(trip_list, key=lambda trip: trip.time)

            if len(trip_list) > 0:
                context = {
                    'trip_list': trip_list,
                    'origin': requested_origin,
                    'destination': requested_destination,
                    'current_day': requested_date,
                    'previous_day': previous_day,
                    'next_day': next_day,
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

    origins = Trip.objects.values_list('origin', flat=True).distinct()
    destinations = Trip.objects.values_list(
        'destination', flat=True
    ).distinct()
    context['origins'] = origins
    context['destinations'] = destinations
    return render(request, 'home/index.html', context)
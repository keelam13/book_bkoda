from django.shortcuts import render
from trips.models import Trip
from trips.forms import TripSearchForm
from datetime import datetime, date, timedelta


def index(request):
    """ A view to return the index page. """
    # Instantiate the form, populating it with GET data if a search was performed
    form = TripSearchForm(request.GET)

    # Initialize trips queryset. It will be filtered later if the form is valid.
    trips = Trip.objects.all()

    # Initialize default values for context, especially for date navigation
    current_date = date.today()
    prev_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)
    selected_origin = None
    selected_destination = None
    selected_travelers = 1

    # Check if the form is submitted AND valid
    if form.is_valid():
        selected_origin = form.cleaned_data.get('origin')
        selected_destination = form.cleaned_data.get('destination')
        # Use the date from the form, or default to today
        current_date = form.cleaned_data.get('date') or date.today() 
        selected_travelers = form.cleaned_data.get('num_travelers') or 1

        # Update prev/next dates based on the current_date after search
        prev_date = current_date - timedelta(days=1)
        next_date = current_date + timedelta(days=1)

        # Apply filters based on form input
        if selected_origin:
            trips = trips.filter(origin__icontains=selected_origin)
        if selected_destination:
            trips = trips.filter(destination__icontains=selected_destination)
        if current_date: # Filter by the selected date
            trips = trips.filter(date=current_date)

        # Filter by available seats (assuming Trip model has this property)
        # This is a list comprehension because available_seats is a @property
        trips = [trip for trip in trips if trip.available_seats >= selected_travelers]

    # Order the results by time for display
    trips = sorted(trips, key=lambda trip: trip.time)

    context = {
        'form': form, # <--- This is the key: pass the form instance!
        'trips': trips,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'selected_origin': selected_origin,
        'selected_destination': selected_destination,
        'selected_travelers': selected_travelers,
    }
    return render(request, 'home/index.html', context)

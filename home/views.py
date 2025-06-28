from django.shortcuts import render
from trips.models import Trip
from trips.forms import TripSearchForm
from datetime import datetime, date, timedelta


def index(request):
    """ A view to return the index page. """
    default_initial_data = {
        'origin': 'Kabayan, Benguet',
        'destination': 'Baguio City',
    }

    form = TripSearchForm()
    
    if request.method == 'GET' and request.GET:
        form = TripSearchForm(request.GET)
    else:
        form = TripSearchForm(initial=default_initial_data)

    trips = Trip.objects.all()

    current_date = date.today()
    selected_origin = default_initial_data['origin']
    selected_destination = default_initial_data['destination']
    selected_travelers = 1

    if form.is_valid():
        selected_origin = form.cleaned_data.get('origin')
        selected_destination = form.cleaned_data.get('destination')
        current_date = form.cleaned_data.get('departure_date') or date.today() 
        selected_travelers = form.cleaned_data.get('num_travelers') or 1

        if selected_origin:
            trips = trips.filter(origin__icontains=selected_origin)
        if selected_destination:
            trips = trips.filter(destination__icontains=selected_destination)
        if current_date:
            trips = trips.filter(departure_date=current_date)

        trips = [trip for trip in trips if trip.available_seats >= selected_travelers]

    prev_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)

    trips = sorted(trips, key=lambda trip: trip.departure_time)

    context = {
        'form': form,
        'trips': trips,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'selected_origin': selected_origin,
        'selected_destination': selected_destination,
        'selected_travelers': selected_travelers,
        'is_home_page': True,
    }
    return render(request, 'home/index.html', context)

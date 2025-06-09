from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Trip
from .forms import TripSearchForm
from booking.models import Booking


def index(request):
    # This view renders the home page with the initial search form
    form = TripSearchForm() # An empty form for the initial GET request to '/'
    context = {
        'form': form,
        'search_error': messages.get_messages(request), # To display messages on home page if redirected here
    }
    return render(request, 'home/index.html', context)


def find_trip(request):
    reschedule_booking_id = request.GET.get('reschedule_booking_id')
    original_booking = None
    is_rescheduling_mode = False

    if reschedule_booking_id:
        try:
            original_booking = Booking.objects.get(pk=reschedule_booking_id, user=request.user)
            is_rescheduling_mode = True
            messages.info(request, f"You are rescheduling booking {original_booking.booking_reference}. Please select a new trip.")
        except Booking.DoesNotExist:
            messages.error(request, "Invalid booking ID for rescheduling.")
            reschedule_booking_id = None # Clear it if invalid
            is_rescheduling_mode = False
        except Exception as e:
            messages.error(request, f"Error retrieving original booking for reschedule: {e}")
            reschedule_booking_id = None
            is_rescheduling_mode = False

    if is_rescheduling_mode and not request.GET:
        initial_data = {
            'origin': original_booking.trip.origin,
            'destination': original_booking.trip.destination,
            'departure_date': original_booking.trip.date,
            'num_travelers': original_booking.number_of_passengers,
        }
        form = TripSearchForm(initial=initial_data)
    else:
        form = TripSearchForm(request.GET)

    context = {'form': form} 

    if is_rescheduling_mode:
        context['is_rescheduling_mode'] = True
        context['original_booking_id'] = original_booking.id
        context['original_booking'] = original_booking

    if form.is_valid():
        requested_origin = form.cleaned_data.get('origin')
        requested_destination = form.cleaned_data.get('destination')
        requested_date = form.cleaned_data.get('departure_date')
        number_of_passengers = form.cleaned_data.get('num_travelers')
        if is_rescheduling_mode and not number_of_passengers:
             number_of_passengers = original_booking.number_of_passengers

        today = datetime.now().date()
        now = datetime.now()

        # Debugging: Print requested parameters
        print(f"--- Trip Search Debug ---")
        print(f"Requested Origin: {requested_origin}")
        print(f"Requested Destination: {requested_destination}")
        print(f"Requested Date: {requested_date}")
        print(f"Requested Passengers: {number_of_passengers}")
        print(f"Current Date/Time: {now}")


        if requested_date and requested_origin and requested_destination:
            try:
                trip_list_queryset = Trip.objects.filter(
                    origin__icontains=requested_origin,
                    destination__icontains=requested_destination,
                    date=requested_date,
                    available_seats__gte=number_of_passengers
                )

                print(f"Initial queryset count (before time filter): {trip_list_queryset.count()}")
                if not trip_list_queryset.exists():
                    print("No trips found in initial queryset for the given origin, destination, and date.")

                final_trip_list = []
                for trip in trip_list_queryset:
                    trip_datetime = datetime.combine(trip.date, trip.departure_time)

                    # Exclude the original trip if in rescheduling mode
                    if is_rescheduling_mode and original_booking and trip.trip_id == original_booking.trip.trip_id:
                        print(f"Excluding original trip {trip.trip_number} from reschedule options.")
                        continue

                    print(f"Checking trip {trip.trip_number} ({trip.origin} to {trip.destination}) on {trip_datetime}")
                    if trip_datetime >= now:
                        calculated_total_price = trip.price * Decimal(number_of_passengers)
                        calculated_total_price = calculated_total_price.quantize(Decimal('0.01'))

                        trip.total_display_price = calculated_total_price
                        trip.requested_passengers = number_of_passengers

                        final_trip_list.append(trip)
                    else:
                        print(f"Trip {trip.trip_number} is in the past, filtering out.")

                final_trip_list = sorted(final_trip_list, key=lambda trip: trip.departure_time)

                print(f"Final trip list count (after time filter and sorting): {len(final_trip_list)}")

                if len(final_trip_list) > 0:
                    context.update({
                        'trip_list': final_trip_list,
                        'origin': requested_origin,
                        'destination': requested_destination,
                        'current_day': requested_date,
                        'previous_day': requested_date - timedelta(days=1),
                        'next_day': requested_date + timedelta(days=1),
                        'number_of_passengers': int(number_of_passengers)
                    })
                    if is_rescheduling_mode:
                        context['is_rescheduling_mode'] = True
                        context['original_booking_id'] = original_booking.id
                        context['original_booking'] = original_booking

                    return render(request, 'trips/trips.html', context)

                elif requested_date < today:
                    messages.error(
                        request, "Sorry, the date you requested is in the past."
                    )
                else:
                    messages.error(
                        request, "Sorry, there are no trips available yet."
                    )
            except Exception as e:
                messages.error(request, f"An unexpected error occurred during trip search: {e}")
                print(f"General error in find_trip: {e}")
        else:
            messages.error(request, "Please fill in all search fields (Origin, Destination, Date).")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Error in '{field}': {error}")
    
    context['search_error'] = messages.get_messages(request)
    return render(request, 'home/index.html', context)
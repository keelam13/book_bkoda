from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from .models import Trip
from .forms import TripSearchForm
from booking.models import Booking


def find_trip(request):
    reschedule_booking_id = request.GET.get('reschedule_booking_id')
    original_booking = None
    is_rescheduling_mode = False
    fixed_num_travelers = None

    if reschedule_booking_id:
        try:
            original_booking = Booking.objects.get(pk=reschedule_booking_id, user=request.user)
            is_rescheduling_mode = True
            fixed_num_travelers = original_booking.number_of_passengers
            messages.info(request, f"You are rescheduling booking {original_booking.booking_reference}. Please select a new trip.")
        except Booking.DoesNotExist:
            messages.error(request, "Invalid booking ID for rescheduling.")
            reschedule_booking_id = None
            is_rescheduling_mode = False
        except Exception as e:
            messages.error(request, f"Error retrieving original booking for reschedule: {e}")
            reschedule_booking_id = None
            is_rescheduling_mode = False

    form_kwargs = {
        'is_rescheduling_mode': is_rescheduling_mode,
        'fixed_num_travelers': fixed_num_travelers
    }

    form = TripSearchForm(request.GET, **form_kwargs)

    requested_date = None
    requested_origin = None
    requested_destination = None
    number_of_passengers_for_query = 1

    if is_rescheduling_mode and not request.GET:
        initial_data = {
            'origin': original_booking.trip.origin,
            'destination': original_booking.trip.destination,
            'departure_date': original_booking.trip.date,
            'num_travelers': fixed_num_travelers,
        }
        form = TripSearchForm(initial=initial_data, **form_kwargs)
    else:
        form = TripSearchForm(request.GET, **form_kwargs)
    
    if form.is_valid():
        requested_origin = form.cleaned_data.get('origin')
        requested_destination = form.cleaned_data.get('destination')
        if form.cleaned_data.get('departure_date'):
            requested_date = form.cleaned_data.get('departure_date')
        number_of_passengers_for_query = fixed_num_travelers if is_rescheduling_mode else form.cleaned_data.get('num_travelers')
    else:
        try:
            requested_date_str = request.GET.get('departure_date')
            if requested_date_str:
                requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

        requested_origin = request.GET.get('origin')
        requested_destination = request.GET.get('destination')
        try:
            get_num_travelers = request.GET.get('num_travelers')
            if get_num_travelers:
                number_of_passengers_for_query = int(get_num_travelers)
        except (ValueError, TypeError):
            pass

    today_date = timezone.localdate()
    disable_previous_day = (requested_date <= today_date)

    available_dates = []
    if requested_origin and requested_destination and number_of_passengers_for_query:
        now_aware = timezone.now()
        today_trips_dates = Trip.objects.filter(
            origin__icontains=requested_origin,
            destination__icontains=requested_destination,
            date=today_date,
            available_seats__gte=number_of_passengers_for_query
        )
        today_available_trips = [
            trip for trip in today_trips_dates
            if timezone.make_aware(datetime.combine(trip.date, trip.departure_time)) >= now_aware
        ]
        if today_available_trips:
            available_dates.append(today_date)

        future_trips_dates_queryset = Trip.objects.filter(
            origin__icontains=requested_origin,
            destination__icontains=requested_destination,
            date__gt=today_date,
            available_seats__gte=number_of_passengers_for_query
        ).values_list('date', flat=True).distinct().order_by('date')

        for d in future_trips_dates_queryset:
            available_dates.append(d)

    available_dates_str = [d.strftime('%Y-%m-%d') for d in sorted(list(set(available_dates)))]

    last_available_date = None
    if available_dates:
        last_available_date = max(available_dates)

    disable_next_day = False
    next_day_date = requested_date + timedelta(days=1)
    if next_day_date not in available_dates:
        disable_next_day = True

    context = {
        'form': form,
        'origin': requested_origin,
        'destination': requested_destination,
        'current_day': requested_date,
        'previous_day': requested_date - timedelta(days=1),
        'next_day': requested_date + timedelta(days=1),
        'number_of_passengers': int(number_of_passengers_for_query),
        'no_trips_message_type': None,
        'disable_previous_day': disable_previous_day,
        'disable_next_day': disable_next_day,
        'available_dates': available_dates_str,
        'last_available_date': last_available_date.strftime('%Y-%m-%d') if last_available_date else None,
        'is_trips_page': True,
    }

    if is_rescheduling_mode:
        context['is_rescheduling_mode'] = True
        context['original_booking_id'] = original_booking.id
        context['original_booking'] = original_booking

    trip_list = []

    if form.is_valid():
        requested_origin = form.cleaned_data.get('origin')
        requested_destination = form.cleaned_data.get('destination')
        requested_date = form.cleaned_data.get('departure_date')
        number_of_passengers_for_query = fixed_num_travelers if is_rescheduling_mode else form.cleaned_data.get('num_travelers')
        now_aware = timezone.now()

        if requested_date and requested_origin and requested_destination:
            try:
                trip_list_queryset = Trip.objects.filter(
                    origin__icontains=requested_origin,
                    destination__icontains=requested_destination,
                    date=requested_date,
                    available_seats__gte=number_of_passengers_for_query
                )

                for trip in trip_list_queryset:
                    trip_datetime_naive = datetime.combine(trip.date, trip.departure_time)
                    trip_datetime_aware = timezone.make_aware(trip_datetime_naive)

                    if trip_datetime_aware >= now_aware:
                        calculated_total_price = trip.price * Decimal(number_of_passengers_for_query)
                        calculated_total_price = calculated_total_price.quantize(Decimal('0.01'))

                        trip.total_display_price = calculated_total_price
                        trip.requested_passengers = number_of_passengers_for_query

                        trip_list.append(trip)
                    else:
                        pass

                final_trip_list = sorted(trip_list, key=lambda trip: trip.departure_time)

                if len(final_trip_list) > 0:
                    context['trip_list'] = final_trip_list
                    return render(request, 'trips/trips.html', context)

                elif requested_date < now_aware.date():
                    context['no_trips_message_type'] = 'date_in_the_past'
                elif requested_date == now_aware.date():
                    context['no_trips_message_type'] = 'no_trips_today'
                else:
                    context['no_trips_message_type'] = 'no_trips_future'

            except Exception as e:
                messages.error(request, f"An unexpected error occurred during trip search: {e}")
        else:
            messages.error(request, "Please fill in all search fields (Origin, Destination, Date).")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Error in '{field}': {error}")

    if 'trip_list' not in context:
        context['trip_list'] = []

    return render(request, 'trips/trips.html', context)

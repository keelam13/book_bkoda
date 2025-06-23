from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import  messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum

# Import models and forms from your app
from trips.models import Trip
from booking.models import Booking
from staff_app.forms import TripForm

from datetime import datetime

# Helper function to check if a user is staff
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

# --- Dashboard View ---
@login_required
@user_passes_test(is_staff_user, login_url='/accounts/login/')
def staff_dashboard(request):
    """
    Staff Dashboard - Provides an overview and navigation.
    """
    total_trips = Trip.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='PENDING_PAYMENT').count()
    confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()

    total_revenue_confirmed = Booking.objects.filter(payment_status='PAID').aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'total_trips': total_trips,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue_confirmed': total_revenue_confirmed,
        'recent_bookings': Booking.objects.order_by('-booking_date')[:5],
        'upcoming_trips': Trip.objects.order_by('date')[:5],
    }
    return render(request, 'staff_app/dashboard.html', context)


@login_required
def trips_list(request):
    """
    View function to display a list of trips with filtering capabilities,
    and also handle updates and deletions for individual trips via POST requests.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        trip_id = request.POST.get('trip_id')
        if not trip_id:
            messages.error(request, 'Invalid request: Trip ID missing.')
            return redirect('staff_app:trips_list')

        trip = get_object_or_404(Trip, trip_id=trip_id)

        if action == 'update_trip' and trip.date < datetime.now():
            messages.error(request, f'Cannot update past trip {trip.trip_number}. Editing is disallowed for past dates.')
            return redirect('staff_app:trips_list')


        if action == 'update_trip':
            form = TripForm(request.POST, instance=trip)
            if form.is_valid():
                form.save()
                messages.success(request, f'Trip {trip.trip_number} updated successfully!')
            else:
                messages.error(request, 'Error updating trip. Please correct the form errors below.')
        elif action == 'delete_trip':
            trip.delete()
            messages.success(request, f'Trip {trip.trip_number} deleted successfully!')
        else:
            messages.error(request, 'Invalid action for trip operation.')
        return redirect('staff_app:trips_list')
    trips_list = Trip.objects.all()

    filter_date = request.GET.get('date')
    filter_destination = request.GET.get('destination')
    filter_origin = request.GET.get('origin')

    if filter_date:
        try:
            date_obj = datetime.strptime(filter_date, '%Y-%m-%d').date()
            trips_list = trips_list.filter(date=date_obj)
        except ValueError:
            pass

    if filter_destination:
        trips_list = trips_list.filter(destination__icontains=filter_destination)

    if filter_origin:
        trips_list = trips_list.filter(origin__icontains=filter_origin)

    trips_list = trips_list.order_by('date', 'departure_time')

    context = {
        'page_title': 'Trips List',
        'trips': trips_list,
        'filter_date': filter_date,
        'filter_destination': filter_destination,
        'filter_origin': filter_origin,
    }
    return render(request, 'staff_app/trips_list.html', context)
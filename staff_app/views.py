from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum

# Import models and forms from your app
from trips.models import Trip
from booking.models import Booking

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
    View function to display a list of trips.
    This will fetch actual trip data from the database.
    """
    trips_list = Trip.objects.all().order_by('date', 'departure_time')

    context = {
        'page_title': 'Trips List',
        'trips': trips_list,
    }
    return render(request, 'staff_app/trips_list.html', context)
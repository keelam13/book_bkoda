from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from .forms import ProfileForm
from booking.models import Booking
from .models import UserProfile
from manage_booking.utils import paginate_queryset

@login_required
def account_details(request):
    """
    Displays account details for the logged-in user.
    """
    return render(request, 'account/account_details.html')

@login_required
def personal_info(request):
    """
    Displays and handles updates for personal information (UserProfile).
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal information updated successfully!')
        else:
            messages.error(request, 'Error updating personal information. Please check the form.')
    else:
        form = ProfileForm(instance=user_profile)

    template = 'account/personal_info.html'
    context = {
        'form': form,
    }
    return render(request, template, context)

@login_required
def my_bookings(request):
    """
    Displays all bookings for the logged-in user,
    categorizing them into 'upcoming confirmed' and 'other bookings'.
    """
    all_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    now = timezone.now()

    upcoming_confirmed_bookings = []
    other_bookings = []

    pending_payment_bookings = Booking.objects.filter(
        user=request.user,
        status='PENDING_PAYMENT',
        payment_status='PENDING',
        payment_method_type__isnull=False
    ).order_by('booking_date')

    num_pending_payment = pending_payment_bookings.count()

    for booking in all_bookings:
        trip_datetime_naive = datetime.combine(booking.trip.date, booking.trip.departure_time)
        trip_datetime_aware = timezone.make_aware(trip_datetime_naive, timezone.get_current_timezone())

        if booking.status == 'CONFIRMED' and trip_datetime_aware > now:
            upcoming_confirmed_bookings.append(booking)
        else:
            pass

    upcoming_confirmed_bookings.sort(key=lambda b: datetime.combine(b.trip.date, b.trip.departure_time))
    num_upcoming_trips = len(upcoming_confirmed_bookings)

    upcoming_confirmed_bookings_page = paginate_queryset(request, upcoming_confirmed_bookings, items_per_page=3)

    template = 'account/my_bookings.html'
    context = {
        'upcoming_confirmed_bookings_page': upcoming_confirmed_bookings_page,
        'num_upcoming_trips': num_upcoming_trips,
        'pending_payment_bookings': pending_payment_bookings,
        'num_pending_payment': num_pending_payment,
    }
    return render(request, template, context)


@login_required
def booking_detail(request, booking_id):
    """
    Displays detailed information for a single booking belonging to the logged-in user.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    template = 'account/booking_detail.html'
    context = {
        'booking': booking,
    }
    return render(request, template, context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import  messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Sum, Min, Max
from django.views.decorators.http import require_POST
from django.utils import timezone
from trips.models import Trip
from booking.models import Booking, BOOKING_STATUS_CHOICES, PAYMENT_STATUS_CHOICES, REFUND_STATUS_CHOICES, PAYMENT_METHOD_CHOICES
from staff_app.forms import TripForm, BookingForm
from manage_booking.utils import paginate_queryset
from io import StringIO
from .management.commands.generate_trips import Command as GenerateTripsCommand
from .management.commands.cancel_unpaid_bookings import Command as CancelUnpaidBookingsCommand
from .management.commands.cancel_null_bookings import Command as CancelNullBookingsCommand
from datetime import datetime, timedelta
import re


# Helper function to check if a user is staff
def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


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

    # --- Calculate Expired Bookings Count for Dashboard Alert ---
    cutoff_time_for_unpaid = timezone.now() - timedelta(hours=24)

    expired_bookings_count = Booking.objects.filter(
        status='PENDING_PAYMENT',
        payment_status='PENDING',
        booking_date__lt=cutoff_time_for_unpaid
    ).count()

    context = {
        'total_trips': total_trips,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue_confirmed': total_revenue_confirmed,
        'recent_bookings': Booking.objects.order_by('-booking_date')[:5],
        'upcoming_trips': Trip.objects.order_by('date')[:5],
        'expired_bookings_count': expired_bookings_count,
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

        if action == 'update_trip' and trip.date < datetime.now().date():
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

    trip_count = trips_list.count()
    min_date = None
    max_date = None

    if trip_count > 0:
        date_aggregation = trips_list.aggregate(min_date=Min('date'), max_date=Max('date'))
        min_date = date_aggregation['min_date']
        max_date = date_aggregation['max_date']

    trips_list = paginate_queryset(request, trips_list, items_per_page=5)

    context = {
        'page_title': 'Trips List',
        'trips_list': trips_list,
        'filter_date': filter_date,
        'filter_destination': filter_destination,
        'filter_origin': filter_origin,
        'now': datetime.now(),
        'trip_count': trip_count,
        'min_date': min_date,
        'max_date': max_date,
    }
    return render(request, 'staff_app/trips_list.html', context)


@login_required
def bookings_list(request):
    """
    View function to display a list of all bookings with filtering capabilities,
    and also handle updates and deletions for individual bookings via POST requests.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        booking_pk = request.POST.get('booking_pk')

        if not booking_pk:
            messages.error(request, 'Invalid request: Booking ID missing.')
            return redirect('staff_app:bookings_list')

        booking = get_object_or_404(Booking, pk=booking_pk)
        print('Booking:', booking)
        trip_datetime = datetime.combine(booking.trip.date, booking.trip.departure_time)
        if action == 'confirm_reschedule_payment':
            try:
                if booking.is_pending_reschedule():
                    booking.status = 'CONFIRMED'
                    booking.payment_status = 'PAID'
                    booking.is_rescheduled = True
                    booking.save()
                    messages.success(request, f'Reschedule for booking {booking.booking_reference} confirmed successfully!')
                else:
                    messages.error(request, 'Booking cannot be confirmed manually in its current state.')
            except Exception as e:
                messages.error(request, f'An error occurred during reschedule confirmation: {e}')

        elif action == 'update_booking' and trip_datetime < datetime.now():
             messages.error(request, f'Cannot update past booking {booking.booking_reference}. Editing is disallowed for past trip dates.')
             return redirect('staff_app:bookings_list')

        elif action == 'update_booking':
            form = BookingForm(request.POST, instance=booking)

            if form.is_valid():
                form.save(commit=False)
                booking.status = form.cleaned_data['status']
                booking.payment_status = form.cleaned_data['payment_status']
                booking.save(update_fields=['status', 'payment_status'])
                messages.success(request, f'Booking {booking.booking_reference} updated successfully!')
            else:
                messages.error(request, 'Error updating booking. Please correct the form errors below.')
        elif action == 'delete_booking':
            booking.delete()
            messages.success(request, f'Booking {booking.booking_reference} deleted successfully!')
        else:
            messages.error(request, 'Invalid action for booking operation.')

        return redirect('staff_app:bookings_list')

    bookings_list = Booking.objects.all().select_related('trip', 'user').prefetch_related('passengers')


    # Get filter parameters
    filter_trip_number = request.GET.get('trip_number')
    filter_customer_name = request.GET.get('customer_name')
    filter_status = request.GET.get('status')
    filter_trip_date = request.GET.get('trip_date')


    # Apply filters
    if filter_trip_number:
        bookings_list = bookings_list.filter(trip__trip_number__icontains=filter_trip_number)
    
    if filter_customer_name:
        bookings_list = bookings_list.filter(passengers__name__icontains=filter_customer_name).distinct()
    
    if filter_status:
        bookings_list = bookings_list.filter(status__iexact=filter_status)
    
    if filter_trip_date:
        try:
            date_obj = datetime.strptime(filter_trip_date, '%Y-%m-%d').date()
            bookings_list = bookings_list.filter(trip__date=date_obj)
        except ValueError:
            messages.error(request, f"Invalid date format for 'Trip Date'. Please use YYYY-MM-DD. Filter was not applied.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred with the 'Trip Date' filter: {e}")

    # --- Calculate Booking Count and Date Range ---
    bookings_list = bookings_list.order_by('-booking_date')

    booking_count = bookings_list.count()
    min_booking_date = None
    max_booking_date = None

    if booking_count > 0:
        date_aggregation = bookings_list.aggregate(min_date=Min('booking_date'), max_date=Max('booking_date'))
        min_booking_date = date_aggregation['min_date']
        max_booking_date = date_aggregation['max_date']

    # --- Calculate Expired Bookings Count ---
    cutoff_time_for_unpaid = timezone.now() - timedelta(hours=24)
    cutoff_time_for_null = timezone.now() - timedelta(hours=1)

    expired_bookings_count = Booking.objects.filter(
        status='PENDING_PAYMENT',
        payment_status='PENDING',
        booking_date__lt=cutoff_time_for_unpaid
    ).count()

    null_bookings_count = Booking.objects.filter(
        payment_method_type__isnull=True,
        booking_date__lt=cutoff_time_for_null
    ).count()

    bookings_list = paginate_queryset(request, bookings_list, items_per_page=5)

    context = {
        'page_title': 'Bookings List',
        'bookings_list': bookings_list,
        'filter_trip_number': filter_trip_number,
        'filter_customer_name': filter_customer_name,
        'filter_status': filter_status,
        'filter_trip_date': filter_trip_date,
        'today': datetime.now(),
        'BOOKING_STATUS_CHOICES': BOOKING_STATUS_CHOICES,
        'PAYMENT_STATUS_CHOICES': PAYMENT_STATUS_CHOICES,
        'REFUND_STATUS_CHOICES': REFUND_STATUS_CHOICES,
        'PAYMENT_METHOD_CHOICES': PAYMENT_METHOD_CHOICES,
        'booking_count': booking_count,
        'min_booking_date': min_booking_date,
        'max_booking_date': max_booking_date,
        'expired_bookings_count': expired_bookings_count,
        'null_bookings_count': null_bookings_count
    }
    return render(request, 'staff_app/bookings_list.html', context)

@login_required
@require_POST
def generate_trips_view(request):
    """
    View to programmatically run the generate_trips management command.
    """
    out = StringIO()
    err = StringIO()
    try:
        command = GenerateTripsCommand()
        command.stdout = out
        command.stderr = err
        command.handle()

        error_output = err.getvalue().strip()
        if error_output:
            messages.error(request, f"Trip generation completed with warnings/errors: {error_output}")
        else:
            messages.success(request, remove_ansi_codes(out.getvalue().strip()))
            
    except Exception as e:
        messages.error(request, f"An error occurred during trip generation: {e}")
        import traceback
    
    return redirect('staff_app:trips_list')

@login_required
@require_POST
def cancel_unpaid_bookings_view(request):
    """
    View to programmatically run the cancel_unpaid_bookings management command.
    """
    out = StringIO()
    err = StringIO()
    try:
        command = CancelUnpaidBookingsCommand()
        command.stdout = out
        command.stderr = err
        command.handle()
        
        error_output = err.getvalue().strip()
        if error_output:
            messages.error(request, f"Unpaid bookings cancellation completed with warnings/errors: {error_output}")
        else:
            messages.success(request, f"Unpaid bookings cancellation completed successfully: {out.getvalue().strip()}")
            
    except Exception as e:
        messages.error(request, f"An error occurred during unpaid bookings cancellation: {e}")
        import traceback
        print(f"Error in cancel_unpaid_bookings_view: {traceback.format_exc()}")
    
    return redirect('staff_app:bookings_list')


@login_required
@require_POST
def cancel_null_bookings_view(request):
    """
    View to programmatically run the cancel_null_bookings management command.
    """
    out = StringIO()
    err = StringIO()
    try:
        command = CancelNullBookingsCommand()
        command.stdout = out
        command.stderr = err
        command.handle()
        
        error_output = err.getvalue().strip()
        if error_output:
            messages.error(request, f"Null bookings cancellation completed with warnings/errors: {error_output}")
        else:
            messages.success(request, f"Null bookings cancellation completed successfully: {out.getvalue().strip()}")
            
    except Exception as e:
        messages.error(request, f"An error occurred during null bookings cancellation: {e}")
        import traceback
        print(f"Error in cancel_null_bookings_view: {traceback.format_exc()}")
    
    return redirect('staff_app:bookings_list')


@login_required
@user_passes_test(is_staff_user)
def confirm_reschedule_payment(request, pk):
    """
    Staff view to manually confirm a pending payment for a rescheduled booking.
    This view handles the logic directly without a signal.
    """
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        try:
            original_booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            messages.error(request, "Booking not found.")
            return redirect('staff_app:bookings_list')

        if booking.status == 'PENDING_PAYMENT' and booking.payment_status == 'PENDING':
            with transaction.atomic():
                booking.status = 'CONFIRMED'
                booking.payment_status = 'PAID'

                if original_booking.trip_id != booking.trip_id:
                    booking.is_rescheduled = True
                
                booking.save()
                
                messages.success(request, f"Payment for booking {booking.booking_reference} successfully confirmed.")
                return redirect('staff_app:bookings_list')
        else:
            messages.error(request, "This booking cannot be manually confirmed.")
            return redirect('staff_app:bookings_list')

    context = {'booking': booking}
    return render(request, 'staff_app/confirm_reschedule_modal.html', context)
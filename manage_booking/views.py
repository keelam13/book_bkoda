from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from booking.models import Booking, BookingPolicy
from trips.models import Trip
from django.db.models import Prefetch
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def booking_list(request):
    """
    Displays a list of all bookings for the currently logged-in user.
    """
    user_bookings = Booking.objects.filter(
        user=request.user
    ).prefetch_related(
        'passengers'
    ).order_by('-booking_date')

    context = {
        'bookings': user_bookings,
        'title': 'My Bookings'
    }
    return render(request, 'manage_booking/booking_list.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    Displays detailed information for a specific booking.
    Ensures the booking belongs to the logged-in user.
    Calculates if cancellation/rescheduling is allowed based on precise policy.
    """
    booking = get_object_or_404(
        Booking.objects.prefetch_related('passengers', 'trip'),
        pk=booking_id,
        user=request.user
    )

    try:
        policy = BookingPolicy.objects.first()
        if not policy:
            messages.error(request, "No booking policy found. Please configure a policy in the admin.")
            return redirect('some_error_page_or_home')
    except BookingPolicy.DoesNotExist:
        messages.error(request, "No booking policy found. Please configure a policy in the admin.")
        return redirect('some_error_page_or_home')

    can_cancel = False
    can_reschedule = False
    cancellation_fee_applied = False
    rescheduling_charge_applied = False

    eligible_status_for_action = (
        booking.status == 'CONFIRMED' and booking.payment_status == 'PAID'
    )

    time_until_departure_hours = -1

    if booking.trip.date and booking.trip.departure_time:
        departure_datetime_naive = datetime.combine(booking.trip.date, booking.trip.departure_time)

        departure_datetime = timezone.make_aware(departure_datetime_naive)
        
        current_time = timezone.now()

        time_until_departure = departure_datetime - current_time
        time_until_departure_hours = time_until_departure.total_seconds() / 3600

        print(f"\n--- DEBUGGING BOOKING ID: {booking.id} ---")
        print(f"TRIP DATE (naive): {booking.trip.date}")
        print(f"TRIP TIME (naive): {booking.trip.departure_time}")
        print(f"DEPARTURE DATETIME (aware): {departure_datetime}")
        print(f"CURRENT TIME (aware): {current_time}")
        print(f"TIME UNTIL DEPARTURE (timedelta): {time_until_departure}")
        print(f"TIME UNTIL DEPARTURE (HOURS): {time_until_departure_hours}")
        print(f"POLICY: free_cancellation_cutoff_hours: {policy.free_cancellation_cutoff_hours}")
        print(f"POLICY: late_cancellation_cutoff_hours: {policy.late_cancellation_cutoff_hours}")
        print("-------------------------------------------\n")


        if eligible_status_for_action:
            if time_until_departure_hours > policy.free_cancellation_cutoff_hours:
                # Free cancellation/rescheduling
                can_cancel = True
                can_reschedule = True
                messages.info(request, f"Cancellation and rescheduling are free if done more than {policy.free_cancellation_cutoff_hours} hours before departure.")
            elif time_until_departure_hours > policy.late_cancellation_cutoff_hours: # Within 24 hours down to 3 hours
                # Cancellation with 50% fee
                can_cancel = True
                cancellation_fee_applied = True
                messages.info(request, f"Cancellation within {policy.free_cancellation_cutoff_hours} to {policy.late_cancellation_cutoff_hours} hours before departure incurs a {int(policy.late_cancellation_fee_percentage * 100)}% fee.")
                
                # Rescheduling with 15% charge
                can_reschedule = True
                rescheduling_charge_applied = True
                messages.info(request, f"Rescheduling between {policy.free_rescheduling_cutoff_hours} to {policy.late_rescheduling_cutoff_hours} hours before departure incurs a {int(policy.late_rescheduling_charge_percentage * 100)}% charge.")
                
            else: # CANCELLATION POLICY FOR < 3 HOURS: ALLOW CANCEL, NO REFUND
                can_cancel = True # Allow cancellation
                cancellation_fee_applied = False
                messages.warning(request, f"Cancellation is allowed less than {policy.late_cancellation_cutoff_hours} hours before departure, but NO REFUND will be issued.")
                # Rescheduling is NOT allowed
                can_reschedule = False
                messages.warning(request, f"Rescheduling is no longer allowed (less than {policy.late_rescheduling_cutoff_hours} hours before departure).")

        else:
            messages.info(request, "This booking cannot be modified due to its current status or payment status.")


    else:
        messages.error(request, "Departure date or time is missing for this trip, unable to determine modification eligibility.")

    context = {
        'booking': booking,
        'title': f'Booking #{booking.booking_reference}',
        'can_cancel': can_cancel,
        'can_reschedule': can_reschedule,
        'cancellation_fee_applied': cancellation_fee_applied,
        'rescheduling_charge_applied': rescheduling_charge_applied,
        'time_until_departure_hours': time_until_departure_hours,
        'policy': policy,
    }
    return render(request, 'manage_booking/booking_detail.html', context)


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.prefetch_related('trip'),
        pk=booking_id,
        user=request.user
    )

    try:
        policy = BookingPolicy.objects.first()
        if not policy:
            messages.error(request, "No booking policy found. Please configure a policy in the admin.")
            return redirect('some_error_page_or_home')
    except BookingPolicy.DoesNotExist:
        messages.error(request, "No booking policy found. Please configure a policy in the admin.")
        return redirect('some_error_page_or_home')

    can_proceed_with_cancellation = False
    refund_amount = Decimal('0.00')
    cancellation_fee_rate = policy.late_cancellation_fee_percentage 

    eligible_status_for_action = (
        booking.status == 'CONFIRMED' and booking.payment_status == 'PAID'
    )

    if booking.trip.date and booking.trip.departure_time:
        departure_datetime_naive = datetime.combine(booking.trip.date, booking.trip.departure_time)
        departure_datetime = timezone.make_aware(departure_datetime_naive)
        current_time = timezone.now()
        time_until_departure = departure_datetime - current_time
        time_until_departure_hours = time_until_departure.total_seconds() / 3600

        print(f"\n--- DEBUGGING BOOKING ID: {booking.id} ---")
        print(f"TRIP DATE (naive): {booking.trip.date}")
        print(f"TRIP TIME (naive): {booking.trip.departure_time}")
        print(f"DEPARTURE DATETIME (aware): {departure_datetime}")
        print(f"CURRENT TIME (aware): {current_time}")
        print(f"TIME UNTIL DEPARTURE (timedelta): {time_until_departure}")
        print(f"TIME UNTIL DEPARTURE (HOURS): {time_until_departure_hours}")
        print(f"POLICY: free_cancellation_cutoff_hours: {policy.free_cancellation_cutoff_hours}")
        print(f"POLICY: late_cancellation_cutoff_hours: {policy.late_cancellation_cutoff_hours}")
        print("-------------------------------------------\n")


        print(f"DEBUG: Booking ID {booking.id} Status: {booking.status}")
        print(f"DEBUG: Booking ID {booking.id} Payment Status: {booking.payment_status}")
        print(f"DEBUG: Eligible for action: {eligible_status_for_action}")

        if eligible_status_for_action:
            if time_until_departure_hours > policy.free_cancellation_cutoff_hours:
                can_proceed_with_cancellation = True
                refund_amount = booking.total_price # Full refund
                refund_type_message = "FULL"
            elif time_until_departure_hours >= policy.late_cancellation_cutoff_hours:
                can_proceed_with_cancellation = True
                refund_amount = booking.total_price * (1 - cancellation_fee_rate)
                refund_type_message = f"{int((1 - cancellation_fee_rate) * 100)}% (due to late cancellation fee)"
            else:
                can_proceed_with_cancellation = True
                refund_amount = Decimal('0.00') # NO REFUND
                refund_type_message = f"NONE (less than {policy.late_cancellation_cutoff_hours} hours before departure)"
                messages.warning(request, "Cancellation is allowed, but no refund will be issued due to proximity to departure time.")
        else:
            messages.error(request, "This booking cannot be cancelled due to its current status or payment status.")
            refund_type_message = "N/A"
    else:
        messages.error(request, "Departure date or time is missing for this trip, unable to determine cancellation eligibility.")
        refund_type_message = "N/A"


    # --- Handle POST request (Confirm Cancellation) ---
    if request.method == 'POST':
         
        recalc_can_proceed = False
        recalc_refund_amount = Decimal('0.00')
        recalc_refund_type_message = "N/A"

        if booking.trip.date and booking.trip.departure_time:
            departure_datetime_recheck = timezone.make_aware(datetime.combine(booking.trip.date, booking.trip.departure_time))
            time_until_departure_recheck = departure_datetime_recheck - timezone.now()
            time_until_departure_hours_recheck = time_until_departure_recheck.total_seconds() / 3600

            print(f"\n--- DEBUGGING BOOKING ID: {booking.id} ---")
            print(f"TRIP DATE (naive): {booking.trip.date}")
            print(f"TRIP TIME (naive): {booking.trip.departure_time}")
            print(f"DEPARTURE DATETIME (aware): {departure_datetime}")
            print(f"CURRENT TIME (aware): {current_time}")
            print(f"TIME UNTIL DEPARTURE (timedelta): {time_until_departure}")
            print(f"TIME UNTIL DEPARTURE (HOURS): {time_until_departure_hours}")
            print(f"POLICY: free_cancellation_cutoff_hours: {policy.free_cancellation_cutoff_hours}")
            print(f"POLICY: late_cancellation_cutoff_hours: {policy.late_cancellation_cutoff_hours}")
            print("-------------------------------------------\n")


            if eligible_status_for_action:
                if time_until_departure_hours_recheck > policy.free_cancellation_cutoff_hours:
                    recalc_can_proceed = True
                    recalc_refund_amount = booking.total_price
                    recalc_refund_type_message = "FULL"
                elif time_until_departure_hours_recheck >= policy.late_cancellation_cutoff_hours:
                    recalc_can_proceed = True
                    recalc_refund_amount = booking.total_price * (1 - cancellation_fee_rate)
                    recalc_refund_type_message = f"{int((1 - cancellation_fee_rate) * 100)}% (due to late cancellation fee)"
                else: # Allow cancel, no refund
                    recalc_can_proceed = True
                    recalc_refund_amount = Decimal('0.00')
                    recalc_refund_type_message = f"NONE (less than {policy.late_cancellation_cutoff_hours} hours before departure)"

        if not recalc_can_proceed:
            messages.error(request, "Cancellation cannot be processed at this time based on policy or booking status.")
            return redirect('manage_booking:booking_detail', booking_id=booking.id)

        try:
            # Step 1: Process Refund if applicable
            if recalc_refund_amount > 0 and booking.stripe_payment_intent_id:
                if settings.STRIPE_MOCK_REFUNDS:
                    booking.payment_status = 'REFUNDED' if recalc_refund_amount == booking.total_price else 'PARTIALLY_REFUNDED'
                    messages.success(request, f"MOCKED REFUND of Php{recalc_refund_amount} processed successfully (Stripe API call skipped).")
                else:
                    stripe_refund_amount_cents = round(refund_amount * 100)
                    refund = stripe.Refund.create(
                        payment_intent=booking.stripe_payment_intent_id,
                        amount=stripe_refund_amount_cents,
                        metadata={
                            'booking_id': str(booking.id),
                            'booking_reference': booking.booking_reference,
                            'refund_type': recalc_refund_type_message,
                        }
                    )
                    
                    if refund.status == 'succeeded':
                        booking.payment_status = 'REFUNDED' if recalc_refund_amount == booking.total_price else 'PARTIALLY_REFUNDED'
                        messages.success(request, f"Refund of Php{recalc_refund_amount} processed successfully via Stripe.")
                    else:
                        booking.payment_status = 'REFUND_PENDING'
                        messages.warning(request, f"Stripe refund status: {refund.status}. It may still be processing or require review. We will inform you once it's complete.")

            elif recalc_refund_amount > 0 and not booking.stripe_payment_intent_id:
                booking.payment_status = 'REFUND_PENDING_MANUAL'
                messages.info(request, f"Your booking is cancelled. A refund of Php{recalc_refund_amount} is pending manual processing (non-card payment). Please check your email for instructions.")

            else:
                booking.payment_status = 'NO_REFUND'
                messages.info(request, "Your booking has been cancelled. No refund was issued as per policy.")
            
            # Step 2: Update Booking Status
            booking.status = 'CANCELED'
            
            # Step 3: Release Seats (update Trip available_seats)
            if booking.trip.available_seats is not None:
                print(f"DEBUG: Trip ID: {booking.trip.trip_id}")
                print(f"DEBUG: Available seats BEFORE adding: {booking.trip.available_seats}")
                print(f"DEBUG: Passengers to add back: {booking.number_of_passengers}")

                booking.trip.available_seats += booking.number_of_passengers
                # DEBUG PRINT 2: Show seats AFTER addition, before save
                print(f"DEBUG: Available seats AFTER adding (before save): {booking.trip.available_seats}")

                booking.trip.save()

                # DEBUG PRINT 3: Confirm save was attempted
                print(f"DEBUG: Trip.save() called for Trip ID: {booking.trip.trip_id}")
            else:
                messages.warning(request, "Could not update trip available seats as it's null.")
                print(f"DEBUG: Warning - Trip available_seats is NULL for Trip ID: {booking.trip.trip_id}")

            booking.save()
            messages.success(request, f"Booking {booking.booking_reference} has been successfully cancelled.")
            return redirect('manage_booking:booking_detail', booking_id=booking.id)

        except stripe.error.StripeError as e:
            messages.error(request, f"A Stripe error occurred during refund processing: {e}. Please contact support.")
            booking.status = 'CANCELLATION_FAILED'
            booking.payment_status = 'REFUND_FAILED'
            booking.save()
            return redirect('manage_booking:booking_detail', booking_id=booking.id)

        except Exception as e:
            messages.error(request, f"An unexpected error occurred during cancellation: {e}. Please contact support.")
            return redirect('manage_booking:booking_detail', booking_id=booking.id)

    # --- Handle GET request (Display Confirmation Page) ---
    context = {
        'booking': booking,
        'time_until_departure_hours': time_until_departure_hours,
        'refund_amount': refund_amount,
        'can_proceed_with_cancellation': can_proceed_with_cancellation,
        'policy': policy,
    }
    return render(request, 'manage_booking/booking_cancel_confirm.html', context)


@login_required
def booking_reschedule_select_trip(request, booking_id):
    """
    Checks if a booking is eligible for rescheduling and then redirects
    to the main trip search page, indicating reschedule mode.
    """
    original_booking = get_object_or_404(Booking.objects.select_related('trip'), pk=booking_id, user=request.user)

    try:
        policy = BookingPolicy.objects.first()
        if not policy:
            messages.error(request, "No booking policy found. Please configure a policy in the admin.")
            return redirect('manage_booking:booking_detail', booking_id=original_booking.id)
    except BookingPolicy.DoesNotExist:
        messages.error(request, "No booking policy found. Please configure a policy in the admin.")
        return redirect('manage_booking:booking_detail', booking_id=original_booking.id)

    can_reschedule = False
    time_until_departure_hours = -1

    eligible_status_for_action = (
        original_booking.status == 'CONFIRMED' and original_booking.payment_status == 'PAID'
    )

    if original_booking.trip.date and original_booking.trip.departure_time:
        departure_datetime_naive = datetime.combine(original_booking.trip.date, original_booking.trip.departure_time)
        departure_datetime = timezone.make_aware(departure_datetime_naive)
        current_time = timezone.now()
        time_until_departure = departure_datetime - current_time
        time_until_departure_hours = time_until_departure.total_seconds() / 3600

        # Check policy for rescheduling eligibility
        if eligible_status_for_action:
            if time_until_departure_hours > policy.free_rescheduling_cutoff_hours:
                can_reschedule = True
            elif time_until_departure_hours >= policy.late_rescheduling_cutoff_hours:
                can_reschedule = True
            else:
                messages.error(request, f"Rescheduling is no longer allowed (less than {policy.late_rescheduling_cutoff_hours} hours before departure).")
        else:
            messages.error(request, "This booking cannot be rescheduled due to its current status or payment status.")
    else:
        messages.error(request, "Original trip departure date or time is missing, unable to determine rescheduling eligibility.")

    if not can_reschedule:
        return redirect('manage_booking:booking_detail', booking_id=original_booking.id)

    redirect_url = reverse('trips') + f'?reschedule_booking_id={original_booking.id}' \
                                      f'&origin={original_booking.trip.origin}' \
                                      f'&destination={original_booking.trip.destination}' \
                                      f'&departure_date={original_booking.trip.date.strftime("%Y-%m-%d")}' \
                                      f'&num_travelers={original_booking.number_of_passengers}'

    messages.info(request, "Please select a new trip from the list below.")
    return redirect(redirect_url)


@login_required
def booking_reschedule_confirm(request, booking_id, new_trip_id):
    messages.info(request, f"You selected new trip {new_trip_id} for booking {booking_id}. Confirmation logic will go here.")
    return redirect('manage_booking:booking_detail', booking_id=booking_id)
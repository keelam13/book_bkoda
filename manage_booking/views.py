from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from booking.models import Booking
from trips.models import Trip
from django.db.models import Prefetch
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

    can_cancel = False
    can_reschedule = False
    cancellation_fee_applied = False
    rescheduling_charge_applied = False

    eligible_status_for_action = (
        booking.status == 'CONFIRMED' and booking.payment_status == 'PAID'
    )

    if booking.trip.date and booking.trip.departure_time:
        departure_datetime_naive = datetime.combine(booking.trip.date, booking.trip.departure_time)

        departure_datetime = timezone.make_aware(departure_datetime_naive)
        
        current_time = timezone.now()

        time_until_departure = departure_datetime - current_time
        time_until_departure_hours = time_until_departure.total_seconds() / 3600

        if eligible_status_for_action:
            if time_until_departure_hours > 24:
                # Free cancellation/rescheduling
                can_cancel = True
                can_reschedule = True
                messages.info(request, "Cancellation and rescheduling are free if done more than 24 hours before departure.")
            elif time_until_departure_hours > 3: # Within 24 hours down to 3 hours
                # Cancellation with 50% fee
                can_cancel = True
                cancellation_fee_applied = True
                messages.info(request, "Cancellation within 24 to 3 hours before departure incurs a 50% fee.")
                
                # Rescheduling with 15% charge
                can_reschedule = True
                rescheduling_charge_applied = True
                messages.info(request, "Rescheduling within 24 to 3 hours before departure incurs a 15% charge.")
                
            else: # CANCELLATION POLICY FOR < 3 HOURS: ALLOW CANCEL, NO REFUND
                can_cancel = True # Allow cancellation
                cancellation_fee_applied = False
                messages.warning(request, "Cancellation is allowed less than 3 hours before departure, but NO REFUND will be issued.")
                
                # Rescheduling is NOT allowed
                can_reschedule = False
                messages.warning(request, "Rescheduling is no longer allowed (less than 3 hours before departure).")

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
        'time_until_departure_hours': time_until_departure_hours if 'time_until_departure_hours' in locals() else -1,
    }
    return render(request, 'manage_booking/booking_detail.html', context)


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.prefetch_related('trip'),
        pk=booking_id,
        user=request.user
    )

    can_proceed_with_cancellation = False
    refund_amount = Decimal('0.00')
    cancellation_fee_rate = Decimal('0.50')

    eligible_status_for_action = (
        booking.status == 'CONFIRMED' and booking.payment_status == 'PAID'
    )

    if booking.trip.date and booking.trip.departure_time:
        departure_datetime_naive = datetime.combine(booking.trip.date, booking.trip.departure_time)
        departure_datetime = timezone.make_aware(departure_datetime_naive)
        current_time = timezone.now()
        time_until_departure = departure_datetime - current_time
        time_until_departure_hours = time_until_departure.total_seconds() / 3600

        if eligible_status_for_action:
            if time_until_departure_hours > 24:
                can_proceed_with_cancellation = True
                refund_amount = booking.total_price # Full refund
                refund_type_message = "FULL"
            elif time_until_departure_hours > 3: # Between 24 and 3 hours
                can_proceed_with_cancellation = True
                refund_amount = booking.total_price * (1 - cancellation_fee_rate) # 50% refund
                refund_type_message = "50% (due to late cancellation fee)"
            else: # CANCELLATION POLICY FOR < 3 HOURS: ALLOW CANCEL, NO REFUND
                can_proceed_with_cancellation = True
                refund_amount = Decimal('0.00') # NO REFUND
                refund_type_message = "NONE (less than 3 hours before departure)"
                messages.warning(request, "Cancellation is allowed, but no refund will be issued due to proximity to departure time.")
        else:
            messages.error(request, "This booking cannot be cancelled due to its current status or payment status.")
            refund_type_message = "N/A"

    else:
        messages.error(request, "Departure date or time is missing for this trip, unable to determine cancellation eligibility.")
        refund_type_message = "N/A"


    # --- Handle POST request (Confirm Cancellation) ---
    if request.method == 'POST':
        if not can_proceed_with_cancellation:
            messages.error(request, "Cancellation cannot be processed at this time based on policy or booking status.")
            return redirect('manage_booking:booking_detail', booking_id=booking.id)

        try:
            # Step 1: Process Refund if applicable
            if refund_amount > 0 and booking.stripe_payment_intent_id:
                stripe_refund_amount_cents = round(refund_amount * 100)

                refund = stripe.Refund.create(
                    payment_intent=booking.stripe_payment_intent_id,
                    amount=stripe_refund_amount_cents,
                    metadata={
                        'booking_id': str(booking.id),
                        'booking_reference': booking.booking_reference,
                        'refund_type': refund_type_message,
                    }
                )
                
                if refund.status == 'succeeded':
                    booking.payment_status = 'REFUNDED' if refund_amount == booking.total_price else 'PARTIALLY_REFUNDED'
                    messages.success(request, f"Refund of €{refund_amount} processed successfully via Stripe.")
                else:
                    booking.payment_status = 'REFUND_PENDING'
                    messages.warning(request, f"Stripe refund status: {refund.status}. It may still be processing or require review. We will inform you once it's complete.")

            elif refund_amount > 0 and not booking.stripe_payment_intent_id:
                booking.payment_status = 'REFUND_PENDING_MANUAL'
                messages.info(request, f"Your booking is cancelled. A refund of Php{refund_amount} is pending manual processing (non-card payment). Please check your email for instructions.")

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
    }
    return render(request, 'manage_booking/booking_cancel_confirm.html', context)

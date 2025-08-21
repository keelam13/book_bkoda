from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from booking.models import Booking, BookingPolicy
from booking.forms import BillingDetailsForm
from my_account.models import UserProfile
from trips.models import Trip
from booking.views import _get_payment_method_context
from django.db.models import Prefetch
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .utils import paginate_queryset
from booking.utils import send_booking_email
from .booking_service import _calculate_reschedule_financials, _create_new_rescheduled_booking

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def all_bookings_list(request):
    """
    Displays a list of all bookings for the currently logged-in user.
    """
    all_bookings = Booking.objects.filter(
        user=request.user,
        payment_method_type__isnull=False
    ).order_by('-trip__date', '-trip__departure_time')

    all_bookings_page = paginate_queryset(request, all_bookings, items_per_page=3)

    template = 'manage_booking/all_bookings_list.html'
    context = {
        'all_bookings_page': all_bookings_page,
        'num_all_bookings': all_bookings.count(),
    }
    return render(request, template, context)

@login_required
def confirmed_bookings_list(request):
    """
    Displays a list of all confirmed bookings for the currently logged-in user.
    """
    confirmed_bookings = Booking.objects.filter(
        user=request.user,
        status='CONFIRMED',
        payment_status='PAID'
    ).order_by('-trip__date', '-trip__departure_time')

    confirmed_bookings_page = paginate_queryset(request, confirmed_bookings, items_per_page=3)

    template = 'manage_booking/confirmed_bookings.html'
    context = {
        'confirmed_bookings_page': confirmed_bookings_page,
        'num_confirmed_bookings': confirmed_bookings.count(),
    }
    return render(request, template, context)

@login_required
def pending_payment_list(request):
    """
    Displays a list of all pending payment bookings for the currently logged-in user.
    """
    pending_payment_bookings = Booking.objects.filter(
        user=request.user,
        status='PENDING_PAYMENT',
        payment_status='PENDING',
        payment_method_type__isnull=False
    ).order_by('-trip__date', '-trip__departure_time')

    pending_payment_bookings_page = paginate_queryset(request, pending_payment_bookings, items_per_page=3)

    template = 'manage_booking/pending_payment.html'
    context = {
        'pending_payment_bookings_page': pending_payment_bookings_page,
        'num_pending_payment_bookings': pending_payment_bookings.count(),
    }
    return render(request, template, context)

@login_required
def pending_or_refunded_bookings_list(request):
    """
    Displays a list of pending refund or refunded bookings for the currently logged-in user.
    """
    pending_refund_bookings = Booking.objects.filter(
        user=request.user,
        refund_status='PENDING'
    ).order_by('-trip__date', '-trip__departure_time')

    refunded_bookings = Booking.objects.filter(
        user=request.user,
        refund_status='COMPLETED'
    ).order_by('-trip__date', '-trip__departure_time')

    pending_refund_bookings_page = paginate_queryset(request, pending_refund_bookings, items_per_page=3)
    refunded_bookings_page = paginate_queryset(request, refunded_bookings, items_per_page=3)

    template = 'manage_booking/pending_or_refunded_bookings.html'
    context = {
        'pending_refund_bookings_page': pending_refund_bookings_page,
        'num_pending_refund_bookings': pending_refund_bookings.count(),
        'refunded_bookings_page': refunded_bookings_page,
        'num_refunded_bookings': refunded_bookings.count(),
    }
    return render(request, template, context)

@login_required
def canceled_bookings_list(request):
    """
    Displays a list of all canceled bookings for the currently logged-in user.
    """
    canceled_bookings = Booking.objects.filter(
        user=request.user,
        status='CANCELED',
        payment_method_type__isnull=False
    ).order_by('-trip__date', '-trip__departure_time')

    canceled_bookings_page = paginate_queryset(request, canceled_bookings, items_per_page=3)

    template = 'manage_booking/canceled_bookings_list.html'
    context = {
        'canceled_bookings_page': canceled_bookings_page,
        'num_canceled_bookings': canceled_bookings.count(),
    }
    return render(request, template, context)

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

    default_next_url = reverse('manage_booking:confirmed_bookings')
    return_url = request.GET.get('next', default_next_url)

    policy = BookingPolicy.objects.first()
    if not policy:
            messages.error(request, "No booking policy found. Please configure a policy in the admin.")
            return redirect('home')

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
            # Cancellation Logic
            if time_until_departure_hours > policy.free_cancellation_cutoff_hours:
                can_cancel = True
                messages.info(request, f"Cancellation is free if done more than {policy.free_cancellation_cutoff_hours} hours before departure.")
            elif time_until_departure_hours >= policy.late_cancellation_cutoff_hours:
                can_cancel = True
                cancellation_fee_applied = True
                messages.info(request, f"Cancellation within {policy.free_cancellation_cutoff_hours} to {policy.late_cancellation_cutoff_hours} hours before departure incurs a {int(policy.late_cancellation_fee_percentage * 100)}% fee.")
            else: # < policy.late_cancellation_cutoff_hours
                can_cancel = True # Allow cancellation
                cancellation_fee_applied = False # No refund will be issued
                messages.warning(request, f"Cancellation is allowed less than {policy.late_cancellation_cutoff_hours} hours before departure, but NO REFUND will be issued.")

            # Rescheduling Logic
            if time_until_departure_hours > policy.free_rescheduling_cutoff_hours:
                can_reschedule = True
                messages.info(request, f"Rescheduling is free if done more than {policy.free_rescheduling_cutoff_hours} hours before departure.")
            elif time_until_departure_hours >= policy.late_rescheduling_cutoff_hours:
                can_reschedule = True
                rescheduling_charge_applied = True
                messages.info(request, f"Rescheduling between {policy.free_rescheduling_cutoff_hours} to {policy.late_rescheduling_cutoff_hours} hours before departure incurs a {int(policy.late_rescheduling_charge_percentage * 100)}% charge.")
            else: # < policy.late_rescheduling_cutoff_hours
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
        'return_url': return_url,
    }
    return render(request, 'manage_booking/booking_detail.html', context)


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.prefetch_related('trip'),
        pk=booking_id,
        user=request.user
    )

    policy = BookingPolicy.objects.first()
    if not policy:
        messages.error(request, "No booking policy found. Please configure a policy in the admin.")
        return redirect('some_error_page_or_home')

    can_proceed_with_cancellation = False
    refund_amount = Decimal('0.00')
    cancellation_fee_rate = policy.late_cancellation_fee_percentage
    refund_type_message = "N/A"

    eligible_status_for_action = (
        booking.status == 'CONFIRMED' and booking.payment_status == 'PAID'
    )

    if booking.is_rescheduled:
        if booking.original_departure_time:
            departure_datetime = booking.original_departure_time
        else:
            departure_datetime = timezone.make_aware(datetime.combine(booking.trip.date, booking.trip.departure_time))
    else:
        departure_datetime = timezone.make_aware(datetime.combine(booking.trip.date, booking.trip.departure_time))

    current_time = timezone.now()
    time_until_departure = departure_datetime - current_time
    time_until_departure_hours = time_until_departure.total_seconds() / 3600

    print(f"\n--- DEBUGGING BOOKING ID: {booking.id} ---")
    print(f"Original Departure Time (aware): {booking.original_departure_time}")
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


    # --- Handle POST request (Confirm Cancellation) ---
    if request.method == 'POST':
        recalc_can_proceed = False
        recalc_refund_amount = Decimal('0.00')
        recalc_refund_type_message = "N/A"

        if booking.is_rescheduled:
            if booking.original_departure_time:
                departure_datetime_recheck = booking.original_departure_time
            else:
                departure_datetime_recheck = timezone.make_aware(datetime.combine(booking.trip.date, booking.trip.departure_time))
        else:
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
            with transaction.atomic():
            # Step 1: Process Refund if applicable
                if recalc_refund_amount > 0:
                    if booking.stripe_payment_intent_id:
                        if settings.STRIPE_MOCK_REFUNDS:
                            messages.success(request, f'REFUND of Php{recalc_refund_amount} is being processed. An email is sent to for more details.')
                            booking.refund_status = 'COMPLETED'
                            booking.refund_amount = recalc_refund_amount
                            send_booking_email(booking, email_type='refund_processing')
                        else:
                            stripe_refund_amount_cents = round(refund_amount * 100)
                            try:
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
                                    booking.refund_status = 'COMPLETED'
                                    booking.refund_amount = recalc_refund_amount
                                    messages.success(request, f"Refund of Php{recalc_refund_amount:.2f} processed successfully via Stripe.")
                                else:
                                    booking.refund_status = 'PENDING'
                                    messages.warning(request, f"Stripe refund status: {refund.status}. It may still be processing or require review. We will inform you once it's complete.")
                            except stripe.error.StripeError as e:
                                messages.error(request, f"A Stripe error occurred during refund processing: {e}. Please contact support.")
                                booking.refund_status = 'FAILED'
                                booking.save()
                                return redirect('manage_booking:booking_detail', booking_id=booking.id)

                    else:
                        booking.refund_status = 'PENDING'
                        booking.refund_amount = recalc_refund_amount
                        send_booking_email(booking, email_type='refund_processing')
                        messages.info(request, f"Your booking is cancelled. A refund of Php{recalc_refund_amount:.2f} is pending manual processing (non-card payment). Please check your email for instructions.")

                else:
                    booking.refund_status = 'NONE'
                    booking.refund_amount = Decimal('0.00')
                    messages.info(request, "Your booking has been cancelled. No refund was issued as per policy.")

                booking.status = 'CANCELED'
                send_booking_email(booking, email_type='cancellation')

                if booking.trip.available_seats is not None:
                    print(f"DEBUG: Trip ID: {booking.trip.trip_id}")
                    print(f"DEBUG: Available seats BEFORE adding: {booking.trip.available_seats}")
                    print(f"DEBUG: Passengers to add back: {booking.number_of_passengers}")

                    booking.trip.available_seats += booking.number_of_passengers
                    print(f"DEBUG: Available seats AFTER adding (before save): {booking.trip.available_seats}")

                    booking.trip.save()
                    print(f"DEBUG: Trip.save() called for Trip ID: {booking.trip.trip_id}")
                else:
                    messages.warning(request, "Could not update trip available seats as it's null.")
                    print(f"DEBUG: Warning - Trip available_seats is NULL for Trip ID: {booking.trip.trip_id}")

                booking.save()
                messages.success(request, f"Booking {booking.booking_reference} has been successfully cancelled.")
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
        'refund_type_message': refund_type_message,
    }
    return render(request, 'manage_booking/booking_cancel_confirm.html', context)


@login_required
def booking_reschedule_select_trip(request, booking_id):
    """
    Checks if a booking is eligible for rescheduling and then redirects
    to the main trip search page, indicating reschedule mode.
    """
    original_booking = get_object_or_404(Booking.objects.select_related('trip'), pk=booking_id, user=request.user)

    policy = BookingPolicy.objects.first()
    if not policy:
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

    # messages.info(request, "Please select a new trip from the list below.")
    return redirect(redirect_url)


@login_required
def booking_reschedule_confirm(request, booking_id, new_trip_id):
    original_booking = get_object_or_404(Booking.objects.select_related('trip'), pk=booking_id, user=request.user)
    new_trip = get_object_or_404(Trip, pk=new_trip_id)
    num_passengers = original_booking.number_of_passengers

    policy = BookingPolicy.objects.first()
    if not policy:
        messages.error(request, "No booking policy found. Please configure a policy in the admin.")
        return redirect('manage_booking:booking_detail', booking_id=original_booking.id)
    
    payment_context = _get_payment_method_context(new_trip)
    if payment_context['is_offline_payment_disallowed']:
        messages.warning(request, f"For bookings within {payment_context['offline_payment_cutoff_hours']} hours of departure, only Card payments are accepted to ensure immediate confirmation.")

    if not (original_booking.status == 'CONFIRMED' and original_booking.payment_status == 'PAID'):
        messages.error(request, "This booking cannot be rescheduled due to its current status or payment status.")
        return redirect('manage_booking:booking_detail', booking_id=original_booking.id)

    if new_trip.available_seats < num_passengers:
        messages.error(request, f"The selected new trip ({new_trip.trip_number}) does not have enough available seats ({new_trip.available_seats}) for {original_booking.number_of_passengers} passengers.")
        redirect_url = reverse('trips') + f'?reschedule_booking_id={original_booking.id}' \
                                          f'&origin={original_booking.trip.origin}' \
                                          f'&destination={original_booking.trip.destination}' \
                                          f'&departure_date={original_booking.trip.date.strftime("%Y-%m-%d")}' \
                                          f'&num_travelers={num_passengers}'
        return redirect(redirect_url)

    if original_booking.trip.trip_id == new_trip.trip_id:
        messages.warning(request, "You cannot reschedule to the same trip. Please select a different one.")
        redirect_url = reverse('trips') + f'?reschedule_booking_id={original_booking.id}' \
                                          f'&origin={original_booking.trip.origin}' \
                                          f'&destination={original_booking.trip.destination}' \
                                          f'&departure_date={original_booking.trip.date.strftime("%Y-%m-%d")}' \
                                          f'&num_travelers={num_passengers}'
        return redirect(redirect_url)

    financials = _calculate_reschedule_financials(original_booking, new_trip, policy)
    amount_to_pay = financials['amount_to_pay']
    amount_to_refund = financials['amount_to_refund']
    new_total_price = amount_to_pay + financials['original_total_price']
    reschedule_type_message = financials['reschedule_type_message']
    time_until_new_departure = payment_context['time_until_departure']

    first_passenger_email = ''
    first_passenger_contact_number = ''
    if original_booking.passengers.exists():
        first_passenger = original_booking.passengers.first()
        first_passenger_email = first_passenger.email if first_passenger.email else ''
        first_passenger_contact_number = first_passenger.contact_number if first_passenger.contact_number else ''

    if reschedule_type_message == "Not Allowed (too close to departure)":
        messages.error(request, f"Rescheduling is no longer allowed (less than {policy.late_rescheduling_cutoff_hours} hours before original departure).")
        return redirect('manage_booking:booking_detail', booking_id=original_booking.id)

    if request.method == 'GET':
        payment_intent = None
        client_secret = None

        if request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            billing_form = BillingDetailsForm(request=request, initial={
            'billing_name': user_profile.default_name or request.user.get_full_name() or request.user.username,
            'billing_email': user_profile.default_email or request.user.email,
            'billing_phone': user_profile.default_phone_number,
            'billing_street_address1': user_profile.default_street_address1,
            'billing_street_address2': user_profile.default_street_address2,
            'billing_city': user_profile.default_city,
            'billing_postcode': user_profile.default_postcode,
            'billing_country': user_profile.default_country,
            })
        else:
            billing_form = BillingDetailsForm()

        if amount_to_pay > 0:
            try:
                stripe_amount = int(amount_to_pay * 100)
                payment_intent = stripe.PaymentIntent.create(
                    amount=stripe_amount,
                    currency="php",
                    metadata={
                        'booking_id': str(original_booking.id),
                        'new_trip_id': str(new_trip.trip_id),
                        'action': 'reschedule_payment',
                    },
                )
                original_booking.payment_intent_id = payment_intent.id
                client_secret = payment_intent.client_secret
                original_booking.save()

            except stripe.error.StripeError as e:
                messages.error(request, f"Error initializing payment: {e}")
                return redirect('manage_booking:booking_detail', booking_id=original_booking.id)

        context = {
            'original_booking': original_booking,
            'new_trip': new_trip,
            'policy': policy,
            'reschedule_type_message': reschedule_type_message,
            'original_total_price': financials['original_total_price'],
            'new_total_price_base': financials['new_total_price_base'],
            'fare_difference': financials['fare_difference'],
            'rescheduling_charge': financials['rescheduling_charge'],
            'amount_to_pay': amount_to_pay,
            'amount_to_refund': amount_to_refund,
            'new_total_price': new_total_price,
            'num_passengers': num_passengers,
            'first_passenger_email': first_passenger_email,
            'first_passenger_contact_number': first_passenger_contact_number,
            'client_secret': client_secret,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'billing_form': billing_form,
            **payment_context
        }
        return render(request, 'manage_booking/booking_reschedule_confirm.html', context)

    elif request.method == 'POST':
        selected_payment_method = request.POST.get('payment_method')
        payment_intent_id = request.POST.get('payment_intent_id')
        billing_form = BillingDetailsForm(request.POST, request=request)

        financials_post = _calculate_reschedule_financials(original_booking, new_trip, policy)
        amount_to_pay_post = financials_post['amount_to_pay']
        amount_to_refund_post = financials_post['amount_to_refund']

        new_booking_params = {
            'total_price': financials_post['original_total_price'] + financials_post['rescheduling_charge'],
        }

        if amount_to_pay_post <= 0:
            new_booking_params.update({
                'status': 'CONFIRMED',
                'payment_status': 'PAID',
                'payment_method_type': 'FREE_RESCHEDULE',
            })

            new_booking = _create_new_rescheduled_booking(
            request, 
            original_booking, 
            new_trip,
            new_booking_params
            )

            messages.success(request, f"Booking {original_booking.booking_reference} successfully rescheduled for free!")
            send_booking_email(original_booking, email_type='rescheduled_confirmation')
            return redirect(reverse('manage_booking:booking_detail', args=[new_booking.id]))

        elif amount_to_pay_post > 0:
            if selected_payment_method == 'CARD':
                if not billing_form.is_valid():
                    messages.error(request, "Please correct the billing address errors.")
                    context = {
                        'original_booking': original_booking,
                        'new_trip': new_trip,
                        'policy': policy,
                        'reschedule_type_message': reschedule_type_message,
                        'original_total_price': financials['original_total_price'],
                        'new_total_price_base': financials['new_total_price_base'],
                        'fare_difference': financials['fare_difference'],
                        'rescheduling_charge': financials['rescheduling_charge'],
                        'amount_to_pay': amount_to_pay,
                        'amount_to_refund': amount_to_refund,
                        'num_passengers': num_passengers,
                        'client_secret': None,
                        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                        'billing_form': billing_form,
                    }
                    return render(request, 'manage_booking/booking_reschedule_confirm.html', context)

                if payment_intent_id:
                    try:
                        stripe.api_key = settings.STRIPE_SECRET_KEY
                        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                        if payment_intent.status == 'succeeded':
                            expected_amount_cents = int(amount_to_pay * 100)
                            if payment_intent.amount != expected_amount_cents:
                                messages.error(request, "Payment amount mismatch. Please contact support.")
                                return redirect(reverse('manage_booking:booking_reschedule_confirm', args=[booking_id, new_trip_id]))

                            new_booking_params.update({
                                'status': 'CONFIRMED',
                                'payment_status': 'PAID',
                                'stripe_payment_intent_id': payment_intent.id,
                                'payment_method_type': 'CARD',
                            })

                            new_booking = _create_new_rescheduled_booking(
                                request,
                                original_booking,
                                new_trip,
                                new_booking_params
                                )

                            messages.success(request, f"Booking {new_booking.booking_reference} successfully rescheduled! Please check your email for details.")
                            send_booking_email(new_booking, email_type='rescheduled_confirmation')
                            return redirect(reverse('manage_booking:booking_detail', args=[new_booking.id]))

                        elif payment_intent.status in ['requires_payment_method', 'requires_confirmation', 'requires_action', 'processing']:
                            messages.error(request, "Payment is still pending or requires further action. Please try again.")
                            return redirect(reverse('manage_booking:booking_reschedule_confirm', args=[booking_id, new_trip_id, ]))
                        else:
                            messages.error(request, f"Payment failed with status: {payment_intent.status}. Please try again.")
                            return redirect(reverse('manage_booking:booking_reschedule_confirm', args=[booking_id, new_trip_id]))

                    except stripe.error.StripeError as e:
                        messages.error(request, f"Stripe error: {e}")
                        return redirect(reverse('manage_booking:booking_reschedule_confirm', args=[booking_id, new_trip_id]))
                    except Exception as e:
                        messages.error(request, f"An unexpected error occurred: {e}")
                        return redirect(reverse('manage_booking:booking_reschedule_confirm', args=[booking_id, new_trip_id]))
                else:
                    messages.error(request, "Payment needs to be completed via the payment form.")
                    return redirect(reverse('manage_booking:booking_reschedule_confirm', args=[booking_id, new_trip_id]))
            elif selected_payment_method in ['CASH', 'GCASH']:
                new_booking_params.update({
                    'status': 'PENDING_PAYMENT',
                    'payment_status': 'PENDING',
                    'payment_method_type': selected_payment_method
                })

                new_booking = _create_new_rescheduled_booking(
                    request,
                    original_booking,
                    new_trip,
                    new_booking_params
                )

                messages.success(request, f"Booking {new_booking.booking_reference} successfully rescheduled to {new_trip.trip_number}! Please complete payment via the selected method to confirm your booking.")
                send_booking_email(new_booking, email_type='pending_payment_instructions')
                return redirect(reverse('manage_booking:booking_detail', args=[new_booking.id]))

        else:
            try:
                with transaction.atomic():
                    if amount_to_refund_post > 0:
                        if settings.STRIPE_MOCK_REFUNDS:
                            messages.success(request, f"REFUND of Php{amount_to_refund_post:.2f} is being processed. Please check your email for more details..")
                            send_booking_email(original_booking, email_type='pending_refund')
                            original_booking.refund_status = 'COMPLETED'
                            original_booking.refund_amount = amount_to_refund_post
                        elif original_booking.stripe_payment_intent_id:
                            stripe_refund_amount_cents = round(amount_to_refund_post * 100)
                            try:
                                refund = stripe.Refund.create(
                                    payment_intent=original_booking.stripe_payment_intent_id,
                                    amount=stripe_refund_amount_cents,
                                    metadata={
                                        'booking_id': str(original_booking.id),
                                        'new_trip_id': str(new_trip.id),
                                        'refund_for_reschedule': 'true',
                                    }
                                )
                                if refund.status == 'succeeded':
                                    original_booking.refund_status = 'COMPLETED'
                                    original_booking.refund_amount = amount_to_refund_post
                                    messages.success(request, f"Refund of Php{amount_to_refund_post:.2f} processed successfully via Stripe.")
                                else:
                                    original_booking.refund_status = 'PENDING'
                                    messages.warning(request, f"Stripe refund status: {refund.status}. It may still be processing or require review.")
                            except stripe.error.StripeError as e:
                                messages.error(request, f"A Stripe error occurred during refund processing: {e}. Please contact support.")
                                original_booking.refund_status = 'FAILED'
                                original_booking.save() #
                                return redirect('manage_booking:booking_detail', booking_id=original_booking.id)
                        else:
                            original_booking.refund_status = 'PENDING'
                            original_booking.refund_amount = amount_to_refund_post
                            send_booking_email(original_booking, email_type='pending_refund')
                            messages.info(request, f"Your booking is rescheduled. A refund of Php{amount_to_refund_post:.2f} is pending manual processing. Please check your email for instructions.")
                    else:
                        messages.info(request, "No additional payment or refund required for this reschedule.")
                        original_booking.refund_status = 'NONE'
                        original_booking.refund_amount = Decimal('0.00')

                    original_booking.trip.available_seats += original_booking.number_of_passengers
                    original_booking.trip.save()

                    new_trip.available_seats -= num_passengers
                    new_trip.save()

                    original_booking.trip = new_trip
                    original_booking.number_of_passengers = num_passengers
                    original_booking.total_price = original_total_price + rescheduling_charge_post
                    original_booking.status = 'CONFIRMED'
                    original_booking.payment_status = 'PAID'
                    original_booking.save()

                    messages.success(request, f"Booking {original_booking.booking_reference} successfully rescheduled to {new_trip.trip_number}!")
                    return redirect('manage_booking:booking_detail', booking_id=original_booking.id)

            except Exception as e:
                messages.error(request, f"An error occurred during rescheduling: {e}")
                return redirect('manage_booking:booking_detail', booking_id=original_booking.id)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import ProfileForm

from booking.models import Booking

@login_required
def profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileForm(instance=profile)
    bookings = profile.user.booking_set.all().order_by('-booking_date')

    context = {
        'form': form,
        'bookings': bookings,
    }
    return render(request, 'profiles/profile.html', context)

def booking_history(request, booking_reference):
    """
    Render the user's booking history page.
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference)

    messages.info(request, (
        f'This is a past confirmation for booking number {booking_reference}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'booking/booking_success.html'
    context = {
        'booking': booking,
    }

    return render(request, template, context)
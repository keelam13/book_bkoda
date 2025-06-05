from django.contrib import admin
from .models import Booking, Passenger
from trips.models import Trip

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1
    fields = ('name', 'age', 'contact_number', 'email')


class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_reference',
        'user_display',
        'trip_number_display',
        'number_of_passengers',
        'total_price',
        'status',
        'payment_status',
        'booking_date',
    )

    list_filter = (
        'status',
        'payment_status',
        'trip__origin',
        'trip__destination',
        'booking_date',
    )

    search_fields = (
        'booking_reference',
        'user__username',
        'user__email',
        'trip__origin',
        'trip__destination',
        'passengers__name',
    )

    readonly_fields = (
        'booking_date',
        'total_price',
        'booking_reference',
    )

    fieldsets = (
        (None, {
            'fields': ('user', 'trip', 'number_of_passengers')
        }),
        ('Booking Details', {
            'fields': ('total_price', 'booking_reference', 'booking_date'),
        }),
        ('Status Information', {
            'fields': ('status', 'payment_status'),
        }),
    )

    inlines = [PassengerInline]

    def user_display(self, obj):
        return obj.user.username if obj.user else "Anonymous"
    user_display.short_description = 'Booked By'

    def trip_number_display(self, obj):
        return obj.trip.trip_number
    trip_number_display.short_description = 'Trip Number'

admin.site.register(Booking, BookingAdmin)

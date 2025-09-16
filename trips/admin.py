from django.contrib import admin
from .models import Trip
from django.db.models import Sum


class TripAdmin(admin.ModelAdmin):
    """
    Admin interface for the Trip model.

    Provides list display, filtering, search functionality, and inline
    editing for Trip objects.
    Also calculates and displays the total number of seats reserved
    for each trip.
    """
    list_display = (
        'trip_number',
        'origin',
        'destination',
        'date',
        'departure_time',
        'arrival_time',
        'available_seats',
        'price',
        'company_name',
        'bus_number',
        'origin_station',
        'destination_station',
    )

    list_filter = ('origin', 'destination', 'date')
    search_fields = ('trip_number', 'origin', 'destination', 'bus_number')
    ordering = ('-date', '-departure_time')


admin.site.register(Trip, TripAdmin)

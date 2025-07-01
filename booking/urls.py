from django.urls import path
from . import views


urlpatterns = [
    path(
        'book/<int:trip_id>/<int:number_of_passengers>/',
        views.book_trip,
        name='book_trip'
        ),
    path(
        'payment/<int:booking_id>/',
        views.process_payment,
        name='process_payment'
        ),
    path(
        'booking_success/<int:booking_id>/',
        views.booking_success,
        name='booking_success'
        ),
]

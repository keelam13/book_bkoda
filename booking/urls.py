from django.urls import path
from . import views


urlpatterns = [
    path('book/<int:trip_id>/<int:number_of_passengers>/', views.book_trip, name='book_trip'),
    path('booking_succes/<int:booking_id>/', views.booking_success, name='booking_success'),
]

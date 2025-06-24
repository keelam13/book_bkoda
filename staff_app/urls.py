from django.urls import path
from . import views

app_name = 'staff_app'

urlpatterns = [
    path('', views.staff_dashboard, name='dashboard'),
    path('trips/', views.trips_list, name='trips_list'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('generate-trips/', views.generate_trips_view, name='generate_trips'),
    path('cancel-unpaid-bookings/', views.cancel_unpaid_bookings_view, name='cancel_unpaid_bookings'),
]
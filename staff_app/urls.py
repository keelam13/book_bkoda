from django.urls import path
from . import views

app_name = 'staff_app'

urlpatterns = [
    path('', views.staff_dashboard, name='dashboard'),
    path('trips/', views.trips_list, name='trips_list'),
    path('bookings/', views.bookings_list, name='bookings_list'),
]
from django.urls import path
from . import views

app_name = 'manage_booking'

urlpatterns = [
    #path('', views.confirmed_bookings_list, name='confirmed_bookings_list'),
    path('confirmed_bookings/', views.confirmed_bookings_list, name='confirmed_bookings'),
    path('pending_payment/', views.pending_payment_list, name='pending_payment'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<int:booking_id>/reschedule/', views.booking_reschedule_select_trip, name='booking_reschedule_select_trip'),
    path('<int:booking_id>/reschedule/confirm/<int:new_trip_id>/', views.booking_reschedule_confirm, name='booking_reschedule_confirm'),
]
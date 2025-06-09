from django.urls import path
from . import views

app_name = 'manage_booking'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<int:booking_id>/reschedule/', views.booking_reschedule_select_trip, name='booking_reschedule_select_trip'),
    path('<int:booking_id>/reschedule/confirm/<int:new_trip_id>/<int:number_of_passengers>/', views.booking_reschedule_confirm, name='booking_reschedule_confirm'),
]
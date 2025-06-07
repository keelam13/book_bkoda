from django.urls import path
from . import views

app_name = 'manage_booking' # Namespace for URLs

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
]
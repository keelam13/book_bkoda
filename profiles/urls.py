from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # path('', views.profile, name='profile'),    
    path('account_details/', views.account_details, name='account_details'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.find_trip, name='trips'),
]

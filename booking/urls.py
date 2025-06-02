from django.urls import path
from . import views


urlpatterns = [
    path('book/<int:trip_id>/<int:number_of_passengers>/', views.book_trip, name='book_trip')
]
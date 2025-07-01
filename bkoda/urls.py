"""
URL configuration for bkoda project.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('account/', include('my_account.urls', namespace='account')),
    path('staff/', include('staff_app.urls')),
    path('', include('home.urls')),
    path('trips/', include('trips.urls')),
    path('booking/', include('booking.urls')),
    path('manage/', include('manage_booking.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'bkoda.views.custom_404_view'
handler500 = 'bkoda.views.custom_500_view'

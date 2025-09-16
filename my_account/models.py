from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    default_name = models.CharField(max_length=50, blank=True, null=True)
    default_phone_number = models.CharField(
        max_length=15, blank=True, null=True)
    default_email = models.EmailField(max_length=254, blank=True, null=True)
    default_street_address1 = models.TextField(
        max_length=20, blank=True, null=True)
    default_street_address2 = models.TextField(
        max_length=20, blank=True, null=True)
    default_city = models.CharField(max_length=100, blank=True, null=True)
    default_postcode = models.CharField(max_length=20, blank=True, null=True)
    default_country = CountryField(
        blank_label='Country *', blank=True, null=True)

    def __str__(self):
        return self.user.username

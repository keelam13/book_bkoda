from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    email = models.EmailField(max_length=20, blank=False, null=False)
    street_address1 = models.TextField(max_length=20, blank=False, null=False)
    street_address2 = models.TextField(max_length=20, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    postcode = models.CharField(max_length=20, blank=False, null=False)
    country = CountryField(blank_label='Country *', blank=False, null=False)

    def __str__(self):
        return self.user.username

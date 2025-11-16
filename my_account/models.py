from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from django_countries.fields import CountryField


PH_POSTAL_CODE_REGEX = r'^\d{4}$'

postal_code_validator = RegexValidator(
    regex=PH_POSTAL_CODE_REGEX,
    message='Postal code must be a valid 4-digit Philippine format \
        (e.g., 1000).',
    code='invalid_postal_code'
)

PHONE_REGEX = r'^\+?\d{9,15}$'

phone_number_validator = RegexValidator(
    regex=PHONE_REGEX,
    message='Phone number must be entered in international format \
        (e.g., +63917xxxxxxx) and be between 9 and 15 digits.',
    code='invalid_phone_number'
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    default_name = models.CharField(max_length=50, blank=True, null=True)
    default_phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[phone_number_validator]
    )
    default_email = models.EmailField(max_length=254, blank=True, null=True)
    default_street_address1 = models.CharField(
        max_length=225, blank=True, null=True)
    default_street_address2 = models.CharField(
        max_length=225, blank=True, null=True)
    default_city = models.CharField(max_length=100, blank=True, null=True)
    default_postcode = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[postal_code_validator]
    )
    default_country = CountryField(
        blank_label='Country *', blank=True, null=True)

    def __str__(self):
        return self.user.username

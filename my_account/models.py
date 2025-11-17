from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from django_countries.fields import CountryField


# NOTE: This regex is currently restricted to the Philippine
# 4-digit numeric format.
# It MUST be updated to dynamic international validation in future dev.
PH_POSTAL_CODE_REGEX = r'^\d{4}$'

postal_code_validator = RegexValidator(
    regex=PH_POSTAL_CODE_REGEX,
    message='Postal code must be a valid 4-digit Philippine format \
        (e.g., 1000).',
    code='invalid_postal_code'
)

# NOTE: This regex is currently restricted to the Philippine
# mobile number format.
# It MUST be updated to dynamic international validation in future dev.
PH_PHONE_REGEX = r'^(\+639|09)\d{9}$'

phone_number_validator = RegexValidator(
    regex=PH_PHONE_REGEX,
    message="Phone number must be entered in the format: \
        '+639xxxxxxxxx' or '09xxxxxxxxx'. Up to 13 digits allowed.",
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
        # Developer Note: This validation is statically set for PH.
        # See PH_PHONE_REGEX definition above.
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
        # Developer Note: This validation is statically set for PH.
        # See PH_POSTAL_CODE_REGEX definition above.
        validators=[postal_code_validator]
    )
    default_country = CountryField(
        blank_label='Country *', blank=True, null=True)

    def __str__(self):
        return self.user.username

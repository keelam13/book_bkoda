from django import template
from datetime import datetime

register = template.Library()


@register.filter
def is_before_now(date, time):
    """Checks if a date and time are before the current datetime."""
    now = datetime.now()
    trip_datetime = datetime.combine(date, time)
    return trip_datetime < now

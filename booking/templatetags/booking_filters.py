from django import template

register = template.Library()


@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return None


@register.filter
def concat_strings(value1, value2):
    """Concatenates two values as strings."""
    return str(value1) + str(value2)


@register.filter
def mul(value, arg):
    "Multiplies the value by the argument"
    return value * arg


@register.filter
def get_status_badge_class(status):
    """Returns Bootstrap badge class based on booking status."""
    status_map = {
        'pending_payment': 'warning',
        'confirmed': 'success',
        'canceled': 'danger',
        'completed': 'primary',
        'no_show': 'secondary',
    }
    return status_map.get(status.lower(), 'info')


@register.filter
def get_payment_status_badge_class(payment_status):
    """Returns Bootstrap badge class based on payment status."""
    status_map = {
        'pending': 'warning',
        'paid': 'success',
        'failed': 'danger',
        'refunded': 'info',
        'none': 'secondary',
    }
    return status_map.get(payment_status.lower(), 'info')

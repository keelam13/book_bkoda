from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    """
    Checks if a string starts with the given argument.
    Usage: {{ my_string|startswith:"prefix" }}
    """
    if not isinstance(value, str):
        value = str(value)

    if not isinstance(arg, str):
        arg = str(arg)

    return value.startswith(arg)
